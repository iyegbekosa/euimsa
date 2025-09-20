from django.urls import path
from . import views

urlpatterns = [
    path("votes/", views.votes_page, name="votes_page"),
    path("vote/initiate/<int:candidate_id>/", views.initiate_vote_payment, name="initiate_vote"),
    path("vote/verify/", views.verify_payment, name="verify_payment"),
    path("vote/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("vote/success/", views.payment_success, name="payment_success"),
]
