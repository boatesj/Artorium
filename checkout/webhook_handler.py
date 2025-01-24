from django.http import HttpResponse
from .models import Order, OrderLineItem
from artworks.models import Artwork
import json
import time
import stripe
import logging

# Configure logger
logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        logger.info(f'Unhandled webhook received: {event["type"]}')
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        try:
            intent = event.data.object
            pid = intent.id
            bag = intent.metadata.get('bag', {})
            save_info = intent.metadata.get('save_info', False)

            # Retrieve the charge object
            stripe_charge = stripe.Charge.retrieve(intent.latest_charge)

            billing_details = stripe_charge.billing_details
            shipping_details = intent.shipping
            grand_total = round(stripe_charge.amount / 100, 2)

            # Clean data in the shipping details
            for field, value in shipping_details.address.items():
                if value == "":
                    shipping_details.address[field] = None

            # Attempt to find an existing order
            order_exists = False
            attempt = 1
            while attempt <= 5:
                try:
                    order = Order.objects.get(
                        full_name__iexact=shipping_details.name,
                        email__iexact=billing_details.email,
                        phone_number__iexact=shipping_details.phone,
                        country__iexact=shipping_details.address.country,
                        postcode__iexact=shipping_details.address.postal_code,
                        town_or_city__iexact=shipping_details.address.city,
                        street_address1__iexact=shipping_details.address.line1,
                        street_address2__iexact=shipping_details.address.line2,
                        county__iexact=shipping_details.address.state,
                        grand_total=grand_total,
                        original_bag=bag,
                        stripe_pid=pid,
                    )
                    order_exists = True
                    logger.info(f'Order {order.order_number} verified in database.')
                    break
                except Order.DoesNotExist:
                    attempt += 1
                    time.sleep(1)

            if order_exists:
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                    status=200)
            else:
                # Create a new order if none exists
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                logger.info(f'New order created: {order.order_number}')

                for item_id, item_data in json.loads(bag).items():
                    artwork = Artwork.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            artwork=artwork,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data.get('items_by_size', {}).items():
                            order_line_item = OrderLineItem(
                                order=order,
                                artwork=artwork,
                                quantity=quantity,
                            )
                            order_line_item.save()

        except Artwork.DoesNotExist as e:
            logger.error(f'Artwork not found: {e}')
            if order:
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Artwork not found',
                status=500)

        except Exception as e:
            logger.error(f'Error processing payment_intent.succeeded: {e}')
            if order:
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500)

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        logger.warning(f'PaymentIntent failed: {event["data"]["object"]["id"]}')
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
