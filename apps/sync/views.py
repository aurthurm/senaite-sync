from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from apps.sync.models import SyncProgress
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
