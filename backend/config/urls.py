from django.contrib import admin
from django.urls import path

from reports.views import create_report
from risk.views import map_data, map_page
from whatsapp.views import demo_message, demo_page, webhook

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", map_page, name="map"),
    path("api/map/", map_data, name="map-data"),
    path("api/reports/", create_report, name="report-create"),
    path("webhook/whatsapp/", webhook, name="whatsapp-webhook"),
    path("demo/", demo_page, name="demo"),
    path("demo/message/", demo_message, name="demo-message"),
]
