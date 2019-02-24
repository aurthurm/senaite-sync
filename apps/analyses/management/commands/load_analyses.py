from django.core.management.base import BaseCommand
import csv, datetime
import dateutil.parser
import pandas as pd
from apps.analyses.models import *
from apps.patients.models import Patient

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Uploading Analysis ... Please wait! ....'))
        path = kwargs['path']
        with open(path, 'rt') as f:
            analyses = pd.read_csv(f)
            # analyses = analyses[:2]
            i = 1
            for row in analyses.iterrows():

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
                    self.stdout.write(self.style.SUCCESS(f'Added {i} Anayses Resquests'))
                    i+=1
                else:                
                    self.stdout.write(self.style.ERROR(f'Patient {pruid} not found. Corresponding Request was skipped'))


        self.stdout.write(self.style.SUCCESS('DONE'))

# python manage.py load_questions --path /path/to/your/file.csv