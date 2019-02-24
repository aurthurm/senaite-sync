from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify

from apps.patients.models import Patient



RECEIVED = "Received"
VERIFIED = "Verified"
PUBLISHED = "Published"
STATES = (
	(RECEIVED, _("Received")),
	(VERIFIED, _('Verified')),
	(PUBLISHED, _('Published'))
	)

ROCHE = "H12PCAP"
ABBOT = "ABBOT"
KEYWORDS = (
	(ROCHE, _('H12PCAP')),
	(ABBOT, _('ABBOT'))
	)

class Analyses(models.Model):
	patient = models.ForeignKey(
		Patient,
		on_delete=models.PROTECT,
		related_name="analyses_for_patient"
		)
	sid = models.CharField(
		_('Sample ID'),
		unique=True,
		max_length=255
		)
	pruid = models.CharField(
		_('Patient UID'),
		null=True,
		blank=True,
		max_length=255
		)
	result = models.CharField(
		_('Result'),
		null=True,
		blank=True,
		max_length=50
		)
	state = models.CharField(
		_('Review State'),
		max_length=20,
		choices=STATES,
		default=RECEIVED
		)
	date_sampled = models.DateTimeField(
		_("Date Sampled"),
		null=True,
		blank=True,
		)
	date_created = models.DateTimeField(
		_("Date Created"),
		null=True,
		blank=True,
		)
	date_received = models.DateTimeField(
		_("Date Received"),
		null=True,
		blank=True,
		)
	date_captured = models.DateTimeField(
		_("Date Captured"),
		null=True,
		blank=True,
		)
	creator = models.CharField(
		max_length=50,
		null=True,
		blank=True,
		)
	keyword = models.CharField(
		_('Instrument Keyword'),
		max_length=10,
		choices=KEYWORDS,
		default=ROCHE
		)

	def __str__(self):
		return f'{self.result}'

	class Meta:
		verbose_name = _("Analyses")
		verbose_name_plural = _("Analyses")

