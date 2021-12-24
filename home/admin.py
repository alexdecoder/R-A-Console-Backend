from home.models import ContactRequest
from django.contrib import admin


class AdminRequest(admin.ModelAdmin):
    pass


admin.site.register(ContactRequest, AdminRequest)
