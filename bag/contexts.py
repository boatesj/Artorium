from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from artworks.models import Artwork

def bag_contents(request):
    """ Context processor for Artorium shopping bag contents """

    bag_items = []
    total = 0
    artwork_count = 0
    bag = request.session.get('bag', {})

    for item_id, quantity in bag.items():
        artwork = get_object_or_404(Artwork, pk=item_id)
        total += quantity * artwork.price
        artwork_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'artwork': artwork,
        })

    # Calculate delivery as 10% of the total
    delivery = total * Decimal(settings.DELIVERY_PERCENTAGE / 100)

    # Grand total includes the total price of items and delivery cost
    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'artwork_count': artwork_count,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context
