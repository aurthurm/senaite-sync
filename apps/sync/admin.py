from django.contrib import admin
from apps.sync.models import *

class SyncClientsInline(admin.TabularInline):
    model = SyncClients
    max_num = 1

class SyncPatientsInline(admin.TabularInline):
    model = SyncPatients
    max_num = 1

class SyncAnalysisInline(admin.TabularInline):
    model = SyncAnalysis
    max_num = 1

class SyncProgressInline(admin.TabularInline):
    model = SyncProgress
    max_num = 1

class SycnAdmin(admin.ModelAdmin):
    inlines = [
        SyncClientsInline,
        SyncPatientsInline,
        SyncAnalysisInline,
        SyncProgressInline
    ]

    list_display = [
        'station_api',
        'username'
    ]

admin.site.register(SyncLogin, SycnAdmin)