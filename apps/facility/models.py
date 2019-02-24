from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify

class Facility(models.Model):
	name = models.CharField(
		_('Name'),
		max_length=50
		)
	state = models.CharField(
		_('State'),
		max_length=255
		)
	district = models.CharField(
		_('District'),
		max_length=255
		)
	fid = models.CharField(
		_('Facility ZW ID'),
		# unique=True,
		max_length=50
		)
	fuid = models.CharField(
		_('Facility UID'),
		unique=True,
		max_length=255
		)

	def __str__(self):
		return f"{self.name}"

	class Meta:
		verbose_name = _("Facility")
		verbose_name_plural = _("Facilities")
