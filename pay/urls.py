from pay.views import pay_main
from django.urls import path

urlpatterns = [
    path('', pay_main),
]
