import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, "payments/home.html")

def create_checkout_session(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Coffee Donation'},
                'unit_amount': 500,  # $5 in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url="http://127.0.0.1:8000/success",
        cancel_url="http://127.0.0.1:8000/cancel",
    )
    return redirect(session.url, code=303)

def success(request):
    return render(request, "payments/success.html")

def cancel(request):
    return render(request, "payments/cancel.html")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = ""  # Need to sort out my CLI stripe to get this working

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        Payment.objects.update_or_create(
            session_id=session['id'],
            defaults={
                'amount': session['amount_total'],
                'email': session.get('customer_details', {}).get('email'),
                'status': 'paid'
            }
        )

    return HttpResponse(status=200)

from .models import Payment

def donations(request):
    payments = Payment.objects.filter(status="paid").order_by('-created_at')
    return render(request, "payments/donations.html", {"payments": payments})
