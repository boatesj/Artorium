from decimal import Decimal

def bag_contents(request):
    """ Context processor for Artorium shopping bag contents """

    bag_items = []
    total = 0
    artwork_count = 0
    delivery = 0

    # Retrieve the shopping bag from the session
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():
        # Simulate fetching artwork data (replace with actual database query)
        artwork = {
            'id': item_id,
            'title': item_data['title'],
            'price': Decimal(item_data['price']),
        }
        subtotal = artwork['price'] * item_data['quantity']
        total += subtotal
        artwork_count += item_data['quantity']

        # Calculate delivery as 10% of the subtotal for each item
        delivery += (artwork['price'] * Decimal(0.10)) * item_data['quantity']

        bag_items.append({
            'artwork': artwork,
            'quantity': item_data['quantity'],
            'subtotal': subtotal,
        })

    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'artwork_count': artwork_count,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context
