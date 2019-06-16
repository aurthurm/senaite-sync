from django.db import models

VERIFIED = "verified"
PUBLISHED = "published"
ALL = "All"
CATEGORIES = (
	(VERIFIED, 'verified'),
	(PUBLISHED, 'published'),
	(ALL, 'All')
	)

class SyncLogin(models.Model):
	station_api = models.CharField(max_length=11)
	username = models.CharField(max_length=255)
	password = models.CharField(max_length=255)

	class Meta:
		verbose_name = "Sync Detail"
		verbose_name_plural = "Sync Details"

class SyncCatalogue(models.Model):
	login = models.ForeignKey(SyncLogin, on_delete=models.PROTECT) # For AdminSite inlines to work
	api_url = models.CharField(max_length=255)
	page_size = models.PositiveIntegerField()
	iterations = models.PositiveIntegerField()
	descending = models.BooleanField(default=True)
	page_nr = models.PositiveIntegerField()

	class Meta:
		abstract=True

class SyncPatients(SyncCatalogue):
	pass

class SyncClients(SyncCatalogue):
	pass

class SyncAnalysis(SyncCatalogue):
	category = models.CharField(
		max_length=255,
		choices=CATEGORIES,
		default=PUBLISHED
		)

class SyncProgress(models.Model):
	login = models.ForeignKey(SyncLogin, on_delete=models.PROTECT, related_name="sync_progress_login") # For AdminSite inlines to work
	client_done = models.BooleanField(default=False)
	client_total = models.PositiveIntegerField()
	client_count = models.PositiveIntegerField()
	client_synced = models.DateTimeField()
	patient_done = models.BooleanField(default=False)
	patient_total = models.PositiveIntegerField()
	patient_count = models.PositiveIntegerField()
	patient_synced = models.DateTimeField()
	analysis_done = models.BooleanField(default=False)
	analysis_total = models.PositiveIntegerField()
	analysis_count = models.PositiveIntegerField()
	analysis_synced = models.DateTimeField()

class SyncSeletion(models.Model):
	# What to sync
	login = models.ForeignKey(SyncLogin, on_delete=models.PROTECT, related_name="sync_selection_login") # For AdminSite inlines to work
	patients = models.BooleanField(default=False)
	clients = models.BooleanField(default=False)
	analyses = models.BooleanField(default=False)