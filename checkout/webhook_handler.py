import logging
from django.http import HttpResponse

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
        try:
            logger.info(f'Unhandled webhook received: {event["type"]}')
            return HttpResponse(
                content=f'Unhandled webhook received: {event["type"]}',
                status=200)
        except Exception as e:
            logger.error(f'Error handling event: {str(e)}')
            return HttpResponse(
                content='Error handling event',
                status=500)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        try:
            logger.info(f'Payment Intent Succeeded webhook received: {event["type"]}')
            # Add logic to handle the event, like updating order status in your database
            return HttpResponse(
                content=f'Webhook received: {event["type"]}',
                status=200)
        except Exception as e:
            logger.error(f'Error handling payment intent succeeded: {str(e)}')
            return HttpResponse(
                content='Error handling payment intent succeeded',
                status=500)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        try:
            logger.info(f'Payment Intent Failed webhook received: {event["type"]}')
            # Add logic to handle the event, like notifying the user
            return HttpResponse(
                content=f'Webhook received: {event["type"]}',
                status=200)
        except Exception as e:
            logger.error(f'Error handling payment intent failed: {str(e)}')
            return HttpResponse(
                content='Error handling payment intent failed',
                status=500)
