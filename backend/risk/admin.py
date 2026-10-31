from django.contrib import admin

from .models import Area, RiskScore, Schedule

admin.site.register([Area, Schedule, RiskScore])
