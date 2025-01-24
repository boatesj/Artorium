import logging
from django.http import HttpResponse

# Get an instance of a logger
logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        logger.info(f'Webhook received: {event["type"]}')
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
