from .models import Payment, AssociationFee, NewUser, SkillAquisition
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import requests
import io, os
from .utils import get_payment_model_instance
from reportlab.lib.units import mm
from reportlab.lib import colors
from django.core.mail import EmailMessage


@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'user':user
    }
    return render(request, 'dashboard.html', context)


@login_required
def history_view(request):
    user = request.user
    account_statement = Payment.objects.filter(user = request.user)
    context = {
        'user':user,
        'account_statement':account_statement
    }
    return render(request, 'history.html', context)


@login_required
def account_view(request):
    user = request.user
    account_statement = Payment.objects.filter(user = request.user)
    context = {
        'user':user,
        'account_statement':account_statement
    }
    return render(request, 'account.html', context)


def initiate_payment(request):
    fee = AssociationFee.objects.all()
    skill = SkillAquisition.objects.all()
    context = {
        'fee':fee,
        'skill':skill,
    }
    return render(request, 'make_payment.html', context)


def get_amount(request):
    payment_type = request.GET.get('type')
    value = request.GET.get('value')
    amount = None

    if payment_type == 'fee':
        fee = AssociationFee.objects.filter(session=value).first()
        amount = fee.amount if fee else None
    elif payment_type == 'skill':
        skill = SkillAquisition.objects.filter(skill_type=value).first()
        amount = skill.amount if skill else None

    return JsonResponse({'amount': amount})


# def initialize_split_payment(request):
#     if request.method == "POST":
#         try:
#             print("Inside initialize_split_payment")
#             data = request.POST
#             name = data.get('payment_type')
#             email = data.get('email')
#             level = data.get('level')
#             amount = data.get('amount')
            
#             # Log raw POST data
#             print("Raw POST data:", request.POST)
            
#             # Check if amount is valid
#             if not amount or float(amount) <= 0:
#                 return HttpResponse("Invalid amount value.")
            
#             # Convert amount to kobo (cents for USD)
#             amount_kobo = round(float(amount) * 100)  # Convert amount to kobo
#             print("Amount in kobo:", amount_kobo)

#             user = get_object_or_404(NewUser, email=email)
            
#             # Create Payment record
#             payment = Payment.objects.create(
#                 user=user,
#                 level=int(level),
#                 amount=amount,
#                 email=user.email,
#             )

#             # Paystack API headers
#             headers = {
#                 "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#                 "Content-Type": "application/json"
#             }

#             protocol = 'https' if request.is_secure() else 'http'
#             callback_url = f"{protocol}://{request.get_host()}{reverse('paystack_callback')}"
#             payload = {
#                 "email": user.email,
#                 "amount": amount_kobo,
#                 "reference": payment.ref,
#                 "callback_url": callback_url,
#                 "split_code": settings.PAYSTACK_SPLIT_CODE,
#             }

#             # Initialize the payment with Paystack
#             response = requests.post(
#                 "https://api.paystack.co/transaction/initialize",
#                 json=payload,
#                 headers=headers
#             )

#             print("Paystack Response:", response.status_code, response.json())

#             # Parsing the response from Paystack
#             res_data = response.json()

#             if response.status_code == 200 and res_data.get('status'):
#                 return redirect(res_data['data']['authorization_url'])
#             else:
#                 return HttpResponse(f"Paystack error: {res_data.get('message', 'Unknown error')}")

#         except Exception as e:
#             return render(request, 'error.html', {'error_message': str(e)})


# def initialize_split_payment(request):
#     if request.method == "POST":
#         try:
#             data = request.POST
#             name = data.get('payment_type')
#             email = data.get('email')
#             level = data.get('level')
#             amount = float(data.get('amount'))  # from AJAX
#             user = get_object_or_404(NewUser, email=email)
#             payment_type = data.get('payment_type')  # "fee" or "skill"
#             session = data.get('session')  # e.g., "2024/2025"
#             skill = data.get('skill')      # e.g., "CODING"

#             print("Incoming payment_type:", payment_type)
#             print("Incoming session:", session)
#             print("Incoming skill:", skill)

#             payment_for = get_payment_model_instance(payment_type, session if payment_type == "fee" else skill)
#             payment_code = payment_for.payment_code if payment_for else "GEN"

#             print("Resolved payment_for:", payment_for)
#             if payment_for:
#                 print("Resolved payment_code:", payment_for.payment_code)

#             amount_kobo = int(amount * 100)

#             base_amount = (amount - 200) / 1.015
#             new_amount = int(base_amount * 100)

#             if payment_type == 'fee':
#                 payment_for = 'association_fee'
#             elif payment_type == 'skill':
#                 payment_for = 'skill_acquisition'
#             else:
#                 payment_for = None

#             # Save payment
#             payment = Payment.objects.create(
#                 user=user,
#                 level=int(level),
#                 amount=amount,
#                 email=user.email,
#                 name=name,
#                 payment_for=payment_for     
#             )

#             # URL for Paystack callback
#             protocol = 'https' if request.is_secure() else 'http'
#             callback_url = f"{protocol}://{request.get_host()}{reverse('paystack_callback')}"

#             # Get split info from settings
#             split_info = settings.PAYSTACK_SPLITS.get(payment_code, {})
#             flat_share = split_info.get('flat_share', 0)
#             flat_recipient = split_info.get('flat_recipient')
#             main_recipient = split_info.get('main_recipient')
#             sub_recipient = split_info.get('sub_recipient')

#             # Build split only if needed
#             split = None

#             if payment_code == "SKIL":
#                 split = {
#                     "type": "flat",
#                     "currency": "NGN",
#                     "subaccounts": [
#                         {
#                             "subaccount": main_recipient,
#                             "share": new_amount
#                         },
#                     ],
#                     "bearer_type": "account"
#                 }

#             elif payment_code == "COLL":
#                 split = {
#                     "type": "flat",
#                     "currency": "NGN",
#                     "subaccounts": [
#                         {
#                             "subaccount": flat_recipient,
#                             "share": 1475000
#                         },
#                         {
#                             "subaccount": sub_recipient,
#                             "share": 25000
#                         },
#                         {
#                             "subaccount": main_recipient,
#                             "share": 500000
#                         }
#                     ],
#                     "bearer_type": "account"
#                 }

#             # Build payload
#             payload = {
#                 "email": user.email,
#                 "amount": amount_kobo,
#                 "reference": payment.ref,
#                 "callback_url": callback_url,
#             }

#             if split:
#                 payload["split"] = split

#             headers = {
#                 "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#                 "Content-Type": "application/json"
#             }

#             response = requests.post(
#                 "https://api.paystack.co/transaction/initialize",
#                 json=payload,
#                 headers=headers
#             )

#             res_data = response.json()
#             print("Paystack Response:", response.status_code, res_data)

#             if response.status_code == 200 and res_data.get('status'):
#                 return redirect(res_data['data']['authorization_url'])
#             else:
#                 return HttpResponse(f"Paystack error: {res_data.get('message', 'Unknown error')}")

#         except Exception as e:
#             return render(request, 'error.html', {
#                 'error_message': str(e),
#             })


def initialize_split_payment(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method.", status=405)

    try:
        data = request.POST
        name = data.get('payment_type')
        email = data.get('email')
        level = data.get('level')
        amount = float(data.get('amount'))

        user = get_object_or_404(NewUser, email=email)
        payment_type = data.get('payment_type')  # "fee" or "skill"
        session = data.get('session')
        skill = data.get('skill')

        print("Incoming payment_type:", payment_type)
        print("Incoming session:", session)
        print("Incoming skill:", skill)

        # Get relevant payment object (your model for skill or session fees)
        payment_obj = get_payment_model_instance(payment_type, session if payment_type == "fee" else skill)
        payment_code = payment_obj.payment_code if payment_obj else "GEN"
        print("Resolved payment_code:", payment_code)

        # Set standardized `payment_for` for model field
        if payment_type == "fee":
            payment_for_label = "association_fee"
        elif payment_type == "skill":
            payment_for_label = "skill_acquisition"
        else:
            payment_for_label = None

        # Create payment record in DB
        payment = Payment.objects.create(
            user=user,
            level=int(level),
            amount=amount,
            email=user.email,
            name=name,
            payment_for=payment_for_label
        )

        # Prepare Paystack payload
        protocol = 'https' if request.is_secure() else 'http'
        callback_url = f"{protocol}://{request.get_host()}{reverse('paystack_callback')}"
        amount_kobo = int(amount * 100)

        # Prepare split if applicable
        split_info = settings.PAYSTACK_SPLITS.get(payment_code)
        split = None

        if split_info:
            # Compute adjusted share (if needed)
            base_amount = (amount - 200) / 1.015
            new_amount = int(base_amount * 100)

            if payment_code == "SKIL":
                split = {
                    "type": "flat",
                    "currency": "NGN",
                    "subaccounts": [
                        {
                            "subaccount": split_info["main_recipient"],
                            "share": new_amount
                        },
                    ],
                    "bearer_type": "account"
                }

            elif payment_code == "COLL":
                split = {
                    "type": "flat",
                    "currency": "NGN",
                    "subaccounts": [
                        {
                            "subaccount": split_info["flat_recipient"],
                            "share": 1475000
                        },
                        {
                            "subaccount": split_info["sub_recipient"],
                            "share": 25000
                        },
                        {
                            "subaccount": split_info["main_recipient"],
                            "share": 500000
                        }
                    ],
                    "bearer_type": "account"
                }

        # Construct payload
        payload = {
            "email": user.email,
            "amount": amount_kobo,
            "reference": payment.ref,
            "callback_url": callback_url,
        }

        if split:
            payload["split"] = split

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        # Call Paystack
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers
        )

        try:
            print("Raw response:", response.content)
            res_data = response.json()
        except ValueError:
            return HttpResponse(f"Paystack returned an invalid response: {response.text}", status=502)

        print("Paystack Response:", response.status_code, res_data)

        if response.status_code == 200 and res_data.get("status"):
            return redirect(res_data["data"]["authorization_url"])
        else:
            return HttpResponse(f"Paystack error: {res_data.get('message', 'Unknown error')}", status=400)

    except Exception as e:
        return render(request, "error.html", {
            "error_message": str(e),
        })


@csrf_exempt
def paystack_callback(request):
    ref = request.GET.get('reference')
    if not ref:
        return JsonResponse({"status": False, "message": "No reference found in URL"})

    try:
        payment = Payment.objects.get(ref=ref)
    except Payment.DoesNotExist:
        return JsonResponse({"status": False, "message": "Invalid reference"})

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    result = response.json()

    if result['status'] and result['data']['status'] == 'success':
        payment.verified = True
        payment.save()
        return redirect('payment_receipt', ref=payment.ref)
    else:
        return render(request, 'error.html', {"error_message": "Payment not successful."})


# def payment_receipt(request, ref):
#     payment = get_object_or_404(Payment, ref=ref)

#     if not payment.verified:
#         return render(request, "error.html", {"error_message": "Payment not verified."})

#     buffer = io.BytesIO()
#     p = canvas.Canvas(buffer, pagesize=A4)

#     # Insert logo
#     logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
#     if os.path.exists(logo_path):
#         p.drawImage(ImageReader(logo_path), 230, 750, width=120, height=60, preserveAspectRatio=True)

#     # Draw header text
#     p.setFont("Helvetica-Bold", 14)
#     p.drawCentredString(300, 730, "EDO UNIVERSITY IYAMHO MEDICAL STUDENTS ASSOCIATION")

#     # Payment info
#     p.setFont("Helvetica", 12)
#     p.drawString(100, 680, f"Name: {payment.user.get_full_name()}")
#     p.drawString(100, 660, f"Email: {payment.email}")
#     p.drawString(100, 640, f"Matriculation Number: {payment.user.mat_no}")
#     p.drawString(100, 620, f"Amount: NGN {payment.amount}")
#     p.drawString(100, 600, f"Reference: {payment.ref}")
#     p.drawString(100, 580, f"Status: SUCCESSFUL")
#     p.drawString(100, 560, f"Date: {payment.date_created.strftime('%d %B %Y, %I:%M %p')}")
#     # p.drawString(100, 540, f"Description: {payment.payment_for.description if payment.payment_for else 'N/A'}")

#     p.showPage()
#     p.save()

#     buffer.seek(0)
#     response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="payment_receipt.pdf"'
#     return response



def payment_receipt(request, ref):
    payment = get_object_or_404(Payment, ref=ref)

    if not payment.verified:
        return render(request, "error.html", {"error_message": "Payment not verified."})

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setStrokeColor(colors.HexColor("#4a4a4a"))
    p.rect(15*mm, 15*mm, width - 30*mm, height - 30*mm, stroke=1, fill=0)

    p.saveState()
    p.setFont("Helvetica-Bold", 60)
    p.setFillColor(colors.lightgrey)
    p.translate(width/2, height/2)
    p.rotate(90)
    p.drawCentredString(0, 0, "EUIMSA RECEIPT")
    p.restoreState()

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(ImageReader(logo_path), (width/2) - 40, height - 100,
                    width=80, height=50, preserveAspectRatio=True)

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 120,
                        "EDO UNIVERSITY IYAMHO MEDICAL STUDENTS ASSOCIATION")
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, height - 140, "Official Payment Receipt")

    p.line(50, height - 150, width - 50, height - 150)

    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#333333"))
    p.drawString(60, height - 180, "Payment Information")

    p.setFillColor(colors.black)
    p.setFont("Helvetica", 12)
    details = [
        ("Name", payment.user.get_full_name()),
        ("Email", payment.email),
        ("Matriculation Number", getattr(payment.user, "mat_no", "N/A")),
        ("Amount", f"NGN {payment.amount:,.2f}"),
        ("Reference", payment.ref),
        ("Status", "SUCCESSFUL"),
        ("Date", payment.date_created.strftime('%d %B %Y, %I:%M %p')),
    ]

    y = height - 200
    for label, value in details:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(70, y, f"{label}:")
        p.setFont("Helvetica", 11)
        p.drawString(220, y, str(value))
        y -= 25

    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.HexColor("#555555"))
    footer_y = 25*mm
    p.drawCentredString(width/2, footer_y, "Thank you for your payment.")

    # Finalize PDF
    p.showPage()
    p.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    subject = "Your Payment Receipt"
    body = f"Dear {payment.user.get_full_name()},\n\nThank you for your payment. Please find your receipt attached.\n\nRegards,\nEUIMSA"
    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [payment.email])
    email.attach("payment_receipt.pdf", pdf_data, "application/pdf")
    email.send()

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="payment_receipt.pdf"'
    return response
