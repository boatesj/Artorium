from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings


from .forms import OrderForm
from bag.contexts import bag_contents

import stripe


def checkout(request):
    """
    Handle checkout functionality for Artorium.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "Your bag is empty. Please add artworks to proceed.")
        return redirect(reverse('artworks'))

    # Calculate total for Stripe PaymentIntent
    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)  # Stripe expects the amount in cents
    stripe.api_key = stripe_secret_key

    # Create PaymentIntent with Stripe
    try:
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
        return redirect(reverse('view_bag'))

    # Initialize the order form
    order_form = OrderForm()

    # Warn if the public key is missing
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. '
                                  'Did you forget to set it in your environment?')


    # Context and template
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,  # For Stripe Elements
    }

    return render(request, template, context)

