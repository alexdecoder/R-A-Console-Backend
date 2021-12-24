from home.views import home_main
from django.http.response import HttpResponse
from django.urls import path


def test(request):
    return HttpResponse('helloworld')


urlpatterns = [
    path('', home_main)
]
