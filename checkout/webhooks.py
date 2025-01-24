from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe
import logging
import json

from checkout.webhook_handler import StripeWH_Handler

# Configure logger
logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f'Invalid payload: {e}')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f'Invalid signature: {e}')
        return HttpResponse(status=400)
    except json.JSONDecodeError as e:
        logger.error(f'JSON Decode Error: {e}')
        return HttpResponse(status=400)
    except stripe.error.APIConnectionError as e:
        logger.error(f'Stripe API Connection Error: {e}')
        return HttpResponse(status=500)
    except Exception as e:
        logger.error(f'Error constructing event: {e}')
        return HttpResponse(content=str(e), status=400)

    # Log received event
    event_type = event['type']
    logger.info(f'Webhook received: {event_type}')

    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the appropriate event handler
    event_handler = event_map.get(event_type, handler.handle_event)

    # Process the event
    try:
        response = event_handler(event)
    except Exception as e:
        logger.error(f'Error handling event {event_type}: {e}')
        return HttpResponse(status=500)

    return response
