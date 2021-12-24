from api.utils import broadcast_notification
from home.models import ContactRequest
from django.shortcuts import render


def home_main(request):
    notifying = False

    first_name = request.POST.get('fname', None)
    email = request.POST.get('email', None)
    phone = request.POST.get('phone', None)
    last_name = request.POST.get('lname', None)
    req = request.POST.get('request', None)
    if first_name != None and email != None and last_name != None and req != None and phone != None:
        ContactRequest.objects.create(
            first_name=first_name[:25], email=email[:25], phone=phone[:25], last_name=last_name[:25], details=req)

        notifying = True

        broadcast_notification(
            'New contact request', 'A new contact request has been created by ' + first_name + ' ' + last_name + ' with the message: ' + req, 'cr')

    return render(request, 'home/base.html', {'notifying': notifying})
