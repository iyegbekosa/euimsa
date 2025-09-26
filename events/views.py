from django.shortcuts import get_object_or_404, redirect, render
from .models import VoteTransaction, Candidate, Category
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .utils import add_paystack_charges
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import requests
import uuid
import json


PRICE_PER_VOTE = 50  # ₦100 per vote


def votes_page(request):
    categories = Category.objects.prefetch_related("candidates").all()
    return render(request, "event/votes.html", {"categories": categories})


def initiate_vote_payment(request, candidate_id):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate")
        votes = int(request.POST.get("votes", 1))  # default 1 vote if missing

        PRICE_PER_VOTE = 50  # set globally or from settings
        amount = votes * PRICE_PER_VOTE  # total without charges

        # calculate Paystack amount including charges
        paystack_amount = add_paystack_charges(amount)

        # use logged-in user’s email, otherwise manual input
        if request.user.is_authenticated:
            email = request.user.email
        else:
            email = request.POST.get("email")

        if not email or "@" not in email:
            return HttpResponse("A valid email address is required", status=400)

        candidate = get_object_or_404(Candidate, id=candidate_id)

        transaction = VoteTransaction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            candidate=candidate,
            votes=votes,
            amount_paid=paystack_amount / 100,  # store in Naira for clarity
            transaction_ref=str(uuid.uuid4())[:12],  # short unique ref
        )

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        callback_url = request.build_absolute_uri(reverse("verify_payment"))

        payload = {
            "email": email,
            "amount": paystack_amount,  # already in Kobo
            "reference": transaction.transaction_ref,
            "callback_url": callback_url,
            "subaccount": settings.ACCT_EUIMSA_SUB,  # 👈 add your subaccount here
            "bearer": "subaccount",  # ensures subaccount bears the charges
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
        )

        try:
            res_data = response.json()
        except ValueError:
            return HttpResponse(f"Paystack returned invalid response: {response.text}", status=502)

        if response.status_code == 200 and res_data.get("status"):
            return redirect(res_data["data"]["authorization_url"])
        else:
            return HttpResponse(f"Paystack error: {res_data.get('message', 'Unknown error')}", status=400)

    return redirect("votes_page")

def verify_payment(request):
    reference = request.GET.get("reference")
    if not reference:
        return HttpResponse("No transaction reference supplied.", status=400)

    transaction = get_object_or_404(VoteTransaction, transaction_ref=reference)

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data.get("status") and res_data["data"]["status"] == "success":
        transaction.status = "success"
        transaction.save()
        return redirect('payment_success')
    else:
        transaction.status = "failed"
        transaction.save()
        return HttpResponse("error.html")


@csrf_exempt
def paystack_webhook(request):
    if request.method != "POST":
        return HttpResponse("Invalid method", status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        event = payload.get("event")

        if event == "charge.success":
            data = payload.get("data", {})
            reference = data.get("reference")

            if reference:
                transaction = get_object_or_404(VoteTransaction, transaction_ref=reference)
                if transaction.status != "success":  # avoid double count
                    transaction.status = "success"
                    transaction.save()

        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(f"Webhook error: {str(e)}", status=500)

def payment_success(request):
    return render(request, "success.html")



def register_candidate(request):
    if request.method == "POST":
        category_id = request.POST.get("category")
        name = request.POST.get("name")
        picture = request.FILES.get("picture")

        if not category_id or not name:
            messages.error(request, "Category and Name are required.")
            return redirect("register_candidate")

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category.")
            return redirect("register_candidate")

        Candidate.objects.create(
            category=category,
            name=name,
            picture=picture
        )

        messages.success(request, "Candidate registered successfully!")
        return redirect("successful")  

    categories = Category.objects.all()
    return render(request, "event/register_candidate.html", {"categories": categories})


def successful(request):
    return render(request, "event/successful.html")

