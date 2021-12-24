from django.http.response import HttpResponse
from django.shortcuts import render


def pay_main(request):
    return render(request, 'pay/pay.html')
