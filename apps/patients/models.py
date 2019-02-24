from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify

from apps.facility.models import Facility

MALE = "Male"
FEMALE = "Female"
UNKNOWN = "Unknown"
GENDERS = (
	(MALE, _("Male")),
	(FEMALE, _('Female')),
	(UNKNOWN, _('Unknown'))
	)

class Patient(models.Model):
	name = models.CharField(
		_('First Name'),
		max_length=255,
		null=True,
		blank=True
		)
	surname = models.CharField(
		_('Last Name'),
		max_length=255,
		null=True,
		blank=True
		)
	gender = models.CharField(
		_('Gender'),
		max_length=6,
		choices=GENDERS,
		default=""
		)
	dob = models.DateField(
		_('Date of Birth'),
		null=True,
		blank=True
		)
	cpid = models.CharField(
		_('Client Patient ID'),
		null=True,
		blank=True,
		max_length=255
		)
	puid = models.CharField(
		_('Patient UID'),
		unique=True,
		null=True,
		blank=True,
		max_length=255
		)
	pruid = models.CharField(
		_('Primary Referrer UID'),
		null=True,
		blank=True,
		max_length=255
		)
	anonymous = models.BooleanField(
		_('Anonymous'),
		default=False
		)
	facility = models.ForeignKey(
		Facility,
		on_delete=models.PROTECT
		)

	def __str__(self):
		return f'{self.name} {self.surname}'

	class Meta:
		verbose_name = _("Patient")
		verbose_name_plural = _("Patients")
