from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    """
    Handle the checkout process.
    Ensures the shopping bag is not empty and renders the order form.
    """
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "Your bag is empty. Please add artworks to proceed.")
        return redirect(reverse('artworks'))

    # Initialize the order form
    order_form = OrderForm()

    # Context and template
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51QQcASRrm86SQNsGHeUOWCoV6jlZiy2xuJWexom0K3ZwPO6lt5k1sOu2eZ2FoT1o0XrBysNj0eS45R4HwMnVmub300emZrNsxz',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)

