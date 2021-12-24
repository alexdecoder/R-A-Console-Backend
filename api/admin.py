from api.models import Customer, Job, Session
from django.contrib import admin


class AdminJob(admin.ModelAdmin):
    pass


class AdminCustomer(admin.ModelAdmin):
    pass


class AdminSession(admin.ModelAdmin):
    pass


admin.site.register(Customer, AdminCustomer)
admin.site.register(Job, AdminJob)
admin.site.register(Session, AdminSession)
