from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("kind", "area", "review_status", "method", "created_at")
    list_filter = ("kind", "review_status", "area")
    actions = ["confirm", "reject"]

    @admin.action(description="Mark selected as confirmed")
    def confirm(self, request, qs):
        qs.update(review_status="confirmed")

    @admin.action(description="Mark selected as rejected")
    def reject(self, request, qs):
        qs.update(review_status="rejected")
