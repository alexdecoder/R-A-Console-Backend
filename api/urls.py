from api.views import card_activity, contact_requests, create_client, initialize_session, overview_data, payout_balance, query_customer, query_job, save_job_notes, query, view_authorization, webhook
from django.urls import path

urlpatterns = [
    path('', overview_data),
    path('handshake/', initialize_session),
    path('q/job/', query_job),
    path('q/job/update/', save_job_notes),
    path('q/cust/', query_customer),
    path('q/search/', query),
    path('q/balance/payout/', payout_balance),
    path('q/cards/activity/', card_activity),
    path('q/cards/authorization/', view_authorization),
    path('q/site/contact_requests/', contact_requests),
    path('q/cust/create/', create_client),
    path('webhook/', webhook)
]
