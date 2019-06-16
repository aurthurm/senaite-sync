from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from apps.sync.models import *
from apps.sync.utils import sync_senaite_to_stanchion

class SyncProgressView(View):

	def get(self, *args, **kwargs):
		data = {}
		progress = SyncProgress.objects.first()
		data['progress'] = {
			"clients_percent": str(progress.client_count/progress.client_total * 100) + "%",
			"clients_total": progress.client_total,
			"clients_total": progress.client_total,

			"patients_percent":  str(progress.patient_count/progress.patient_total * 100) + "%",
			"patients_total": progress.patient_total,
			"patients_synced": progress.client_synced,

			"analyses_percent":  str(progress.analysis_count/progress.analysis_total * 100) + "%",
			"analyses_total": progress.analysis_total,
			"analyses_synced": progress.client_synced,
		}
		return JsonResponse(data)

class SyncSenaiteView(TemplateView):
	template_name = 'sync/sync.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['progress'] = SyncProgress.objects.first()
		return context

	def post(self, *args, **kwargs):
		data = {}
		_request = self.request.POST
		action = _request.get('action', None)
		# if action and action == "sync":
		# 	sync_senaite_to_stanchion()
		# 	data['message'] = "SUCCESS"
		# else:
		# 	data['message'] = "ERROR"

		try:
			sync_senaite_to_stanchion()
			data['message'] = "SUCCESS"
			data['error'] = ""
		except Exception as e:
			data['message'] = "ERROR"
			data['error'] = str(e)

		return JsonResponse(data)

class Selections(View):
	def get(self, *args, **kwargs):
		data = {}
		selection = SyncSeletion.objects.first()
		sync_analysis = SyncAnalysis.objects.first()

		data['analyses'] = 'true' if selection.analyses else 'false'
		data['clients'] = 'true' if selection.clients else 'false'
		data['patients'] = 'true' if selection.patients else 'false'

		category = sync_analysis.category
		if category == ALL:
			data['published_verified'] = 'true'
			data['verified'] = 'false'
			data['published'] = 'false'
		elif category == VERIFIED:
			data['published_verified'] = 'false'
			data['verified'] = 'true'
			data['published'] = 'false'
		else:
			data['published_verified'] = 'false'
			data['verified'] = 'false'
			data['published'] = 'true'
			
		return JsonResponse(data)

	def post(self, *args, **kwargs):
		data = {}
		selection = SyncSeletion.objects.first()
		sync_analysis = SyncAnalysis.objects.first()

		analysis = True if self.request.POST.get('analyses') == 'true' else False
		clients = True if self.request.POST.get('clients') == 'true' else False
		patients = True if self.request.POST.get('patients') == 'true' else False
		selection.patients = patients
		selection.clients = clients
		selection.analyses = analysis
		selection.save()

		verified = True if self.request.POST.get('verified') == 'true' else False
		published = True if self.request.POST.get('published') == 'true' else False
		published_verified = True if self.request.POST.get('published_verified',) == 'true' else False	

		if published_verified:
			sync_analysis.category = ALL
		elif verified:
			sync_analysis.category = VERIFIED
		else:
			sync_analysis.category = PUBLISHED
		sync_analysis.save()

		data['analyses'] = selection.analyses
		data['clients'] = selection.clients
		data['patients'] = selection.patients
		data['analyses_category'] = sync_analysis.category
		return JsonResponse(data)