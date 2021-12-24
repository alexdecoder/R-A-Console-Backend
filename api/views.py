from datetime import datetime
from home.models import ContactRequest
from json.decoder import JSONDecodeError
from django.http.response import HttpResponse
from api.utils import auth_session, broadcast_notification, get_bal, get_prev_7_rev, get_user_object_from_session
from uuid import uuid4
from api.models import Customer, Session, Job
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
from django.conf import settings

if settings.DEBUG:
    stripe.api_key = "sk_test_8YJXeEwPytVArTAWEGIMF6kx"
else:
    stripe.api_key = 'sk_live_KFpvXYDuDZpW9Cl02qGkvLiZ'

# In the refactored codebase, this isn't a mess


def overview_data(request):
    buffer = {}
    if auth_session(request):
        bal_obj = stripe.Balance.retrieve()
        buffer['general'] = {
            'first_name': get_user_object_from_session(request).first_name,
            'prev7rev': get_prev_7_rev(),
            'payout': float(bal_obj['available'][0]['amount'] / 100),
            'issuing': float(bal_obj['issuing']['available'][0]['amount'] / 100),
        }

        buffer['customers'] = {}
        customers = Customer.objects.all()
        for customer in customers:
            buffer['customers'][str(customer.uuid)] = {
                'name': customer.first_name + ' ' + customer.last_name,
                'balance': get_bal(customer),
                'phoneNumber': customer.number,
            }

        cards = stripe.issuing.Card.list()['data']
        buffer['cards'] = {}
        for card in cards:
            if card['status'] != 'canceled':
                buffer['cards'][card['id']] = {
                    'last4': card['last4'],
                    'expMonth': card['exp_month'],
                    'expYear': card['exp_year'],
                    'cardHolder': card['cardholder']['name'],
                }

        buffer['recentServices'] = {}
        jobs = Job.objects.all().order_by('-job_date')[:20]
        for job in jobs:
            buffer['recentServices'][str(job.job_uuid)] = {
                'title': job.job_title,
                'amount': float(job.job_cost),
                'date': str(job.job_date.month) + '/' + str(job.job_date.day),
                'name': Customer.objects.get(jobs__id=job.id).first_name + ' ' + Customer.objects.get(jobs__id=job.id).last_name,
                'iconId': job.job_category,
            }

        buffer['account'] = {}
        buffer['account']['issuingEvents'] = {}
        issuing_events = stripe.issuing.Authorization.list(limit=5)['data']
        for event in issuing_events:
            buffer['account']['issuingEvents'][event['id']] = {
                'authorized': event['approved'],
                'title': event['merchant_data']['name'],
                'date': str(datetime.fromtimestamp(event['created']).month) + '/' + str(datetime.fromtimestamp(event['created']).day),
                'cardholder': event['card']['cardholder']['name'],
                'last4': event['card']['last4'],
                'amount': float(event['amount'] / -100),
            }
        buffer['account']['accountBalanceEvents'] = {}
        payout_events = stripe.BalanceTransaction.list(
            type='payout')['data'] + stripe.BalanceTransaction.list(
            type='topup')['data']
        payout_events = payout_events[:5]

        for event in payout_events:
            if event['type'] == 'payout' or event['type'] == 'topup':
                buffer['account']['accountBalanceEvents'][event['id']] = {
                    'wasTransferedIn': event['amount'] > 0,
                    'amount': float(event['amount'] / 100),
                    'date': str(datetime.fromtimestamp(event['created']).month) + '/' + str(datetime.fromtimestamp(event['created']).day),
                }

        buffer['contactRequests'] = {}
        for contact_request in ContactRequest.objects.all().order_by('-date'):
            buffer['contactRequests'][str(contact_request.uuid)] = {
                'first_name': contact_request.first_name,
                'last_name': contact_request.last_name,
                'email': contact_request.email,
                'phone': contact_request.phone,
                'details': contact_request.details,
                'date': str(contact_request.date.month) + '/' + str(contact_request.date.day),
            }

        return JsonResponse({'result': 'success', 'value': buffer})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def initialize_session(request):
    body = request.body.decode('utf-8')
    try:
        serialized_body = json.loads(body)
    except TypeError:
        return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})
    except JSONDecodeError:
        return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})

    try:
        prev_id = serialized_body['established_id']

        try:
            session_object = Session.objects.get(session_id=prev_id)
            if session_object.is_valid == True:
                session_object.session_id = uuid4()
                session_object.fcm_token = serialized_body['token']
                session_object.save()

                request.session['authenticated'] = True
                request.session['id'] = str(session_object.session_id)

                session_objects = Session.objects.filter(
                    user__id=session_object.user.id).exclude(session_id=session_object.session_id)
                for session in session_objects:
                    session.delete()

                return JsonResponse({'result': 'success', 'value': 'session_initialized', 'id': str(session_object.session_id)})
            else:
                return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})

        except Session.DoesNotExist:
            return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})

    except KeyError:
        try:
            username = serialized_body['username']
            password = serialized_body['password']
            user_object = authenticate(
                username=username, password=password)

            if user_object != None:
                session_object = Session(user=user_object)
                session_object.fcm_token = serialized_body['token']
                session_object.save()

                request.session['authenticated'] = True
                request.session['id'] = str(session_object.session_id)

                session_objects = Session.objects.filter(
                    user__id=session_object.user.id).exclude(session_id=session_object.session_id)
                for session in session_objects:
                    session.delete()

                return JsonResponse({'result': 'success', 'value': 'session_initialized', 'id': str(session_object.session_id)})
            else:
                return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})

        except KeyError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})


@csrf_exempt
def query_job(request):
    if auth_session(request):
        try:
            query = json.loads(request.body.decode('utf-8'))['query']
            job_object = Job.objects.get(job_uuid=query)
            customer = Customer.objects.get(jobs__id=job_object.id)

            return JsonResponse({'result': 'success', 'value': {
                'name': customer.first_name + ' ' + customer.last_name,
                'balance': get_bal(customer),
                'title': job_object.job_title,
                'uuid': str(job_object.job_uuid),
                'cost': float(job_object.job_cost),
                'isPaid': job_object.job_paid,
                'jobNotes': job_object.job_notes,
                'date': str(job_object.job_date.month) + '/' + str(job_object.job_date.day) + '/' + str(job_object.job_date.year),
                'cust_uuid': str(customer.uuid),
            }})
        except Job.DoesNotExist:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
        except TypeError:
            return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})
        except KeyError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def save_job_notes(request):
    if auth_session(request):
        try:
            query = json.loads(request.body.decode('utf-8'))
            job_object = Job.objects.get(job_uuid=query['job_uuid'])
            job_object.job_notes = query['notes']
            job_object.save()

            return JsonResponse({'result': 'success'})
        except Job.DoesNotExist:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
        except TypeError:
            return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})
        except KeyError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def query_customer(request):
    if auth_session(request):
        try:
            query = json.loads(request.body.decode('utf-8'))['query']
            customer_object = Customer.objects.get(uuid=query)

            response_buffer = {
                'name': customer_object.first_name + ' ' + customer_object.last_name,
                'tab': get_bal(customer_object),
                'address': customer_object.address,
                'phone': customer_object.number,
                'email': customer_object.email,
                'services': {},
            }
            for service in customer_object.jobs.all().order_by('-job_date'):
                response_buffer['services'][str(service.job_uuid)] = {
                    'title': service.job_title,
                    'date':  str(service.job_date.month) + '/' + str(service.job_date.day) + '/' + str(service.job_date.year),
                    'amount': float(service.job_cost),
                    'icon': service.job_category,
                }

            return JsonResponse({'result': 'success', 'value': response_buffer})
        except Customer.DoesNotExist:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
        except TypeError:
            return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})
        except KeyError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def query(request):
    if auth_session(request):
        try:
            query = json.loads(request.body.decode('utf-8'))['query']
            search_results = Customer.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query) | Q(number__icontains=query) | Q(address__icontains=query))

            response_buffer = {}
            for result in search_results:
                response_buffer[str(result.uuid)] = {
                    'name': result.first_name + ' ' + result.last_name,
                    'tab': get_bal(result),
                    'address': result.address,
                    'phone': result.number,
                    'email': result.email,
                }
            return JsonResponse({'result': 'success', 'value': response_buffer})
        except TypeError:
            return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})
        except KeyError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def payout_balance(request):
    if auth_session(request):
        try:
            amount = json.loads(request.body.decode('utf-8'))['payout']
        except TypeError:
            return JsonResponse({'result': 'error', 'value': 'invalid_json_values'})
        except KeyError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})

        try:
            amount = float(amount)
            bal_obj = stripe.Balance.retrieve()

            if float(bal_obj['available'][0]['amount'] / 100) < amount:
                return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
            else:
                stripe.Payout.create(
                    amount=int(amount * 100), currency="usd")
                return JsonResponse({'result': 'success'})
        except ValueError:
            return JsonResponse({'result': 'error', 'value': 'invalid_parameters'})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def card_activity(request):
    if auth_session(request):
        issuing_events = stripe.issuing.Authorization.list()['data']
        response_buffer = {}
        for event in issuing_events:
            response_buffer[event['id']] = {
                'authorized': event['approved'],
                'title': event['merchant_data']['name'],
                'date': str(datetime.fromtimestamp(event['created']).month) + '/' + str(datetime.fromtimestamp(event['created']).day),
                'cardholder': event['card']['cardholder']['name'],
                'last4': event['card']['last4'],
                'amount': float(event['amount'] / -100),
            }
        return JsonResponse({'result': 'success', 'value': response_buffer})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def view_authorization(request):
    if auth_session(request):
        iid = json.loads(request.body.decode('utf-8'))['query']
        authorization = stripe.issuing.Authorization.retrieve(iid)
        response_buffer = {
            'amount': authorization['amount'] / 100,
            'approved': authorization['approved'],
            'method': authorization['authorization_method'].capitalize(),
            'name': authorization['card']['cardholder']['individual']['first_name'] + ' ' + authorization['card']['cardholder']['individual']['last_name'],
            'last4': authorization['card']['last4'],
            'expMonth': authorization['card']['exp_month'],
            'expYear': authorization['card']['exp_year'],
            'merchant': authorization['merchant_data']['name'],
            'category': authorization['merchant_data']['category'],
            'city': authorization['merchant_data']['city'] + ', ' + authorization['merchant_data']['state'],
            'wallet': authorization['wallet']
        }

        return JsonResponse({'result': 'success', 'value': response_buffer})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'issuing_authorization.request':
        auth = event["data"]["object"]
        authorization = stripe.issuing.Authorization.approve(auth['id'])
        broadcast_notification(
            authorization['merchant_data']['name'] + "  •••• " + authorization['card']['last4'], "A payment of $" + str(round(authorization['amount'] / 100, 2)) + ' at ' + authorization['merchant_data']['name'] + ' was authorized by ' + authorization['card']['cardholder']['individual']['first_name'] + ' ' + authorization['card']['cardholder']['individual']['last_name'] + '.', 'auth')
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)


@csrf_exempt
def contact_requests(request):
    if auth_session(request):
        requests = ContactRequest.objects.all().order_by('-date')
        response_buffer = {}
        for event in requests:
            response_buffer[event.id] = {
                'first_name': event.first_name,
                'last_name': event.last_name,
                'date': str(event.date.month) + '/' + str(event.date.day),
                'email': event.email,
                'phone': event.phone,
                'details': event.details,
            }
        return JsonResponse({'result': 'success', 'value': response_buffer})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def create_client(request):
    if auth_session(request):
        query = json.loads(request.body.decode('utf-8'))

        Customer.objects.create(
            first_name=query['first_name'].capitalize(), last_name=query['last_name'].capitalize(), email=query['email'].lower(), number=query['number'], address=query['address'])

        return JsonResponse({'result': 'success'})
    else:
        return JsonResponse({'result': 'error', 'value': 'invalid_credentials'})


@csrf_exempt
def test_view(request):
    return JsonResponse({'result': 'success', 'value': {}})
