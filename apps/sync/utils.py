import requests, json, os, dateutil.parser
import pandas as pd
import numpy as np
from datetime import datetime
from .json2csv import in_memory_json_to_csv
from apps.sync.models import *
from apps.analyses.models import *
from apps.facility.models import *
from apps.patients.models import *

CSV_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def progress_reset():
	#Reset progress before sync
	progress = SyncProgress.objects.first()
	progress.client_done = False
	progress.client_count = 0
	progress.client_total = 1

	progress.patient_done = False
	progress.patient_count = 0
	progress.patient_total = 1

	progress.analysis_done = False
	progress.analysis_count = 0
	progress.analysis_total = 1
	progress.save()

def progress_update(page_nr, portal_type, done):
	page_nr += 1
	progress = SyncProgress.objects.first()
	if portal_type == "clients":
		if done:
			progress.client_done = True
			progress.client_synced = datetime.now()
		progress.client_count = page_nr
	if portal_type == "patients":
		if done:
			progress.patient_done = True
			progress.patient_synced = datetime.now()
		progress.patient_count = page_nr
	if portal_type == "analysis":
		if done:
			progress.analysis_done = True
			progress.analysis_synced = datetime.now()
		progress.analysis_count = page_nr		
	progress.save()

def csv_reducer(unfiltered, portal_type):
	portal_type = portal_type.lower()
	if (portal_type == "analyses") or (portal_type == "analysis"):
		return unfiltered[
			[
			#	"PatientUID",
				"Patient_uid",
				"ClientPatientID",
				"Client",
				"SampleType",
				"getSampleID",
				"Analyses_0_Result",
				"Analyses_0_Unit",
				"Analyses_0_review_state",
				"DateSampled",
				"creation_date",
				"Creator",
				"DateReceived",
				"Analyses_0_ResultCaptureDate",
				"DatePublished",
				"Analyses_0_Instrument",
				"Analyses_0_Keyword",
			]
		]
	elif portal_type == "patients":
		return unfiltered[
			[
				"PrimaryReferrerUID",
				"UID",
				"Firstname",
				"Surname",
				"Gender",
				"BirthDate",
				"ConsentSMS",
				"ClientPatientID",
			]
		]
	elif portal_type == "clients":
		return unfiltered[
		    [
		        "ClientID",
		        "Name",
		        "PhysicalAddress_district",
		        "PhysicalAddress_state",
		        "UID",
		        "id",
		    ]
		]

def truncate_csv(csv_file):
	file = open(csv_file, "w+") 
	file.close()

def to_cvs(json_file, portal_type):
	csv_file = os.path.join(CSV_DIR, 'temp', 'temp.csv')	
	truncate_csv(csv_file)	
	in_memory_json_to_csv(json.dumps(json_file), csv_file)
	unreduced_csv = pd.read_csv(csv_file)
	csv_file = csv_reducer(unreduced_csv, portal_type)
	return csv_file

def get_access_details(portal_type):	
	if portal_type == "patients":
		sync_details = SyncPatients.objects.first()
	if portal_type == "analysis":
		sync_details = SyncAnalysis.objects.first()
	if portal_type == "clients":
		sync_details = SyncClients.objects.first()
	return sync_details

def csv_to_stanchion_db(csv, portal_type):
	if portal_type == "patients":
		for row in csv.iterrows():
		    pruid=row[1]["PrimaryReferrerUID"]
		    try:
		        facility = Facility.objects.get(fuid__exact=pruid)
		    except Facility.DoesNotExist:
		        facility = None

		    if facility != None:
		        Patient.objects.get_or_create(
		            name=row[1]["Firstname"],
		            surname=row[1]["Surname"],
		            gender=row[1]["Gender"],
		            dob=dateutil.parser.parse(row[1]["BirthDate"], ignoretz=True),
		            cpid=row[1]["ClientPatientID"],
		            puid=row[1]["UID"],
		            pruid=row[1]["PrimaryReferrerUID"],
		            anonymous=False,
		            facility=facility
		        )                
		    else:
		    	# say something about the error     
		    	pass     

	if portal_type == "analysis":
		for row in csv.iterrows():

		    pruid=row[1]["Patient_uid"]
		    try:
		        patient = Patient.objects.get(puid__exact=pruid)
		    except Patient.DoesNotExist:
		        patient = None

		    if patient != None:
		        state = row[1]["Analyses_0_review_state"]
		        if state == 'verified':
		            sate = VERIFIED
		        else:
		            state = PUBLISHED

		        keyword = row[1]["Analyses_0_Keyword"]
		        if keyword == "HI2CAP96":
		            keyword = ROCHE
		        else:
		            keyword = ABBOT

		        # self.stdout.write(self.style.SUCCESS(f'Added {pruid} Anayses Resquests'))

		        try:
		            date_sampled = dateutil.parser.parse(row[1]["DateSampled"], ignoretz=False)
		        except TypeError:
		            date_sampled = None

		        try:
		            date_received = dateutil.parser.parse(row[1]["DateReceived"], ignoretz=False)
		        except TypeError:
		            date_received = None

		        try:
		            date_created = dateutil.parser.parse(row[1]["creation_date"], ignoretz=False)
		        except TypeError:
		            date_created = None

		        try:
		            date_captured = dateutil.parser.parse(row[1]["Analyses_0_ResultCaptureDate"], ignoretz=False)
		        except TypeError:
		            date_captured = None

		        Analyses.objects.get_or_create(
		            patient=patient,
		            sid=row[1]["getSampleID"],
		            pruid=row[1]["Patient_uid"],
		            result=row[1]["Analyses_0_Result"],
		            state=state,
		            date_sampled=date_sampled,
		            date_created=date_created,
		            date_received=date_received,
		            date_captured=date_captured,
		            creator=row[1]["Creator"],
		            keyword=keyword
		        )  
		    else:                
		        # say something about the error  
		        pass

	if portal_type == "clients":
		for row in csv.iterrows():
		    Facility.objects.get_or_create(
		        name=row[1]["Name"],
		        state=row[1]["PhysicalAddress_state"],
		        district=row[1]["PhysicalAddress_district"],
		        fid=row[1]["ClientID"],
		        fuid=row[1]["UID"],
		    )

def get_counts(portal_type, api_url, login, sync_details):
	# Get how many objects are in senaite and determine how many pulls for a total sync
	# Also for progress-bar functioning
	print(f"getting counts for {portal_type}")
	page_nr = 0
	page_size = 10
	api_url+=str(page_nr)
	api_data = requests.get(api_url, auth=(login.username, login.password))
	api_data = json.loads(api_data.text)
	iterations = int(np.ceil(int(api_data['total_objects'])/int(sync_details.page_size)))
	progress = SyncProgress.objects.first()
	if portal_type == "clients":
		progress.client_total = iterations
	if portal_type == "patients":
		progress.patient_total = iterations
	if portal_type == "analysis":
		progress.analysis_total = iterations		
	progress.save()

	sync_details.iterations = iterations
	sync_details.save()
	print(f"Done getting counts for {portal_type}")

def get_json_from_api(portal_type, api_url, login, sync_details):
	page_nr = int(sync_details.page_nr)
	iterations = int(sync_details.iterations)
	page_size = int(sync_details.page_size)
	print(portal_type)
	for i in range(iterations):
		api_url+=str(page_nr)
		api_data = requests.get(api_url, auth=(login.username, login.password))
		api_data = json.loads(api_data.text)
		json_objects = api_data['objects']
		csv = to_cvs(json_objects, portal_type)
		csv_to_stanchion_db(csv, portal_type)

	    # Remove previous concatenation before new concatenation : str(i)
		if page_nr < 10:                         
			api_url=api_url[:-1]
		elif page_nr >= 10 and page_nr < 100:
			api_url=api_url[:-2]
		else:
			api_url=api_url[:-3]

		if i == int(sync_details.iterations) - 1:
			done = True
		else:
			done = False
		progress_update(page_nr, portal_type, done)
		page_nr += 1

def update_clients(login, portal_type):
	print("Updating Clients")
	sync_details = get_access_details(portal_type)
	api_url = "http://" + login.station_api + sync_details.api_url + str(sync_details.page_size) + "&page_nr="	
	get_counts(portal_type, api_url, login, sync_details)
	get_json_from_api(portal_type, api_url, login, sync_details)

def update_patients(login, portal_type):
	print("Updating Patients")
	sync_details = get_access_details(portal_type)
	api_url = "http://" + login.station_api + sync_details.api_url + str(sync_details.page_size) + "&page_nr="	
	get_counts(portal_type, api_url, login, sync_details)
	get_json_from_api(portal_type, api_url, login, sync_details)

def update_analyses(login, portal_type):
	print("Updating Analyses")
	sync_details = get_access_details(portal_type)
	api_url = "http://" + login.station_api + sync_details.api_url
	if sync_details.category == "All":
		states = ["verified", "published"]
		for state in states:
			review_state = state
			api_url += str(review_state) + "&sort_order=descending&page_size=" + str(sync_details.page_size)+ "&page_nr="
			get_counts(portal_type, api_url, login, sync_details)
			get_json_from_api(portal_type, api_url, login, sync_details)
	else:
		review_state = sync_details.category
		api_url += str(review_state) + "&sort_order=descending&page_size=" + str(sync_details.page_size) + "&page_nr="
		get_counts(portal_type, api_url, login, sync_details)
		get_json_from_api(portal_type, api_url, login, sync_details)

def sync_senaite_to_stanchion():
	#  Call me and ill do you the magic ::: sync_senaite_to_stanchion()
	progress_reset()	
	login = SyncLogin.objects.first()
	update_clients(login, portal_type="clients")
	update_patients(login, portal_type="patients")
	update_analyses(login, portal_type="analysis")

	# For Future Updates
	# ->> make celecry task for sync_senaite_to_stanchion()