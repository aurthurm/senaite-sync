from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse
import re, json
import dateutil.parser
from django.db.models import Q

from apps.patients.models import Patient
from apps.facility.models import Facility
from apps.analyses.models import Analyses



class Home(TemplateView):
	template_name = 'dashboard.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context


class SearchView(View):
	
	def get(self, *args, **kwargs):
		data = {}
		query = self.request.GET
		target = query.get('target').strip()
		q = query.get('q').strip()

		data['target'] = target
		if target == 'patient':
			names = re.split("\s+", q)
			first_entry = names[0]
			try:
				second_entry = names[1]
			except:
				second_entry = None

			if second_entry:
				patients = Patient.objects.select_related('facility').filter(
						Q(name__icontains=first_entry) & Q(surname__icontains=second_entry) |
						Q(cpid__icontains=first_entry)
					)
			else:
				patients = Patient.objects.select_related('facility').filter(
						Q(name__icontains=first_entry) | Q(cpid__icontains=first_entry)
					)

			collection = []
			for patient in patients:
				multi_analyses = patient.analyses_for_patient.all()
				for item in multi_analyses:
					collection.append({
						"name":item.patient.name + " " + item.patient.surname,
						"gender":item.patient.gender,
						"dob":item.patient.dob,
						"cpid":item.patient.cpid,
						"facility":item.patient.facility.name,
						"province":item.patient.facility.state,
						"district":item.patient.facility.district,
						"sid":item.sid,
						"result":item.result,
						"state":item.state,
						"keyword":item.keyword,
						"creator":item.creator,
						"sampled":str(item.date_sampled)[:10],
						"created":str(item.date_created)[:10],
						"received":str(item.date_received)[:10],
						"captured":str(item.date_captured)[:10],
					})
		else:
			query_analsysis = q
			analyses = Analyses.objects.select_related('patient', 'patient__facility').filter(
					Q(sid__icontains=query_analsysis)
				)
			collection = []
			for item in analyses:
				collection.append({
					"name":item.patient.name + " " + item.patient.surname,
					"gender":item.patient.gender,
					"dob":item.patient.dob,
					"cpid":item.patient.cpid,
					"facility":item.patient.facility.name,
					"province":item.patient.facility.state,
					"district":item.patient.facility.district,
					"sid":item.sid,
					"result":item.result,
					"state":item.state,
					"keyword":item.keyword,
					"creator":item.creator,
					"sampled":str(item.date_sampled)[:10],
					"created":str(item.date_created)[:10],
					"received":str(item.date_received)[:10],
					"captured":str(item.date_captured)[:10],
				})
		data['result'] = collection
		return JsonResponse(data)

class StatsQueyView(View):

	def get(self, *args, **kwargs):
		data = {}
		query = self.request.GET
		start = query.get('start')
		end = query.get('end')
		state = query.get('state')

		if not start or not end or not state:
			data["error"] = "Please select a start date,  end date and review"
			data["result"] = None
			return JsonResponse(data)
		else:
			start = dateutil.parser.parse(start, ignoretz=False)
			end = dateutil.parser.parse(end, ignoretz=False)
			if state != "all":
				analyses = Analyses.objects.select_related('patient', 'patient__facility').filter(
						Q(date_captured__gte=start) & Q(date_captured__lte=end) & Q(state__exact=state)
					)
			else:
				analyses = Analyses.objects.select_related('patient', 'patient__facility').filter(
						Q(date_captured__gte=start) & Q(date_captured__lte=end)
					)

			collection = []
			for item in analyses:
				collection.append({
					"name":item.patient.name + " " + item.patient.surname,
					"gender":item.patient.gender,
					"dob":item.patient.dob,
					"cpid":item.patient.cpid,
					"facility":item.patient.facility.name,
					"province":item.patient.facility.state,
					"district":item.patient.facility.district,
					"sid":item.sid,
					"result":item.result,
					"state":item.state,
					"keyword":item.keyword,
					"creator":item.creator,
					"sampled":str(item.date_sampled)[:10],
					"created":str(item.date_created)[:10],
					"received":str(item.date_received)[:10],
					"captured":str(item.date_captured)[:10],
				})
		data['result'] = collection
		return JsonResponse(data)