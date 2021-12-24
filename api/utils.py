import json
from api.models import Session, Job
from datetime import datetime, timedelta
from django.db.models import Sum
import http.client


def auth_session(request):
    if request.session.get('authenticated', None) != None:
        try:
            session_object = Session.objects.get(
                session_id=request.session.get('id'))

            return session_object.is_valid
        except Session.DoesNotExist:
            return False
    else:
        return False


def get_user_object_from_session(request):
    return Session.objects.get(
        session_id=request.session.get('id')).user


def get_prev_7_rev():
    return float(Job.objects.filter(job_date__gte=datetime.now()-timedelta(days=7), job_paid=True).aggregate(Sum('job_cost'))['job_cost__sum'] or 0.0)


def get_bal(customer):
    return float(customer.jobs.filter(job_paid=False).aggregate(Sum('job_cost'))['job_cost__sum'] or 0.0)


def broadcast_notification(title, message, channel):
    sessions = Session.objects.all()
    for session in sessions:
        connection = http.client.HTTPSConnection('fcm.googleapis.com')
        headers = {'Content-type': 'application/json',
                   'Authorization': 'key=AAAAMNzuD_w:APA91bHVtCci5bMTzfis8bAPGB6rBq0cx9s_DJqToRQjr4yP_0O95Gih2d2p0vCbQJkBam3VZsQM1gvdq8WTNwktzZ7D-2M506y7Ta7TnQQPyhPLuUZ0BI0RW-XOkY0TWM7_Ron8vy4E'}
        body = {
            'to': session.fcm_token,
            'data': {
                'title': title,
                'body': message,
                'channel': channel,
            },
            'android': {
                'priority': 'high'
            }
        }
        connection.request('POST', '/fcm/send', json.dumps(body), headers)
