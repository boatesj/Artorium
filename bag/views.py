from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages
import logging

from artworks.models import Artwork

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')

def add_to_bag(request, artwork_id):
    """ Add a quantity of the specified artwork to the shopping bag """
    artwork = Artwork.objects.get(pk=artwork_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})

    if artwork_id in bag:
        bag[artwork_id] += quantity
        messages.success(request, f'Updated the quantity of "{artwork.title}" to {bag[artwork_id]}.')
    else:
        bag[artwork_id] = quantity
        messages.success(request, f'Added "{artwork.title}" to your bag.')

    request.session['bag'] = bag
    return redirect(redirect_url)

def update_bag(request, artwork_id):
    """ Update the quantity of the specified artwork in the shopping bag """
    quantity = int(request.POST.get('quantity'))
    artwork = Artwork.objects.get(pk=artwork_id)
    bag = request.session.get('bag', {})

    if quantity > 0:
        bag[artwork_id] = quantity
        messages.success(request, f'Updated "{artwork.title}" quantity to {quantity}.')
    else:
        bag.pop(artwork_id, None)
        messages.success(request, f'Removed "{artwork.title}" from your bag.')

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))

# Configure the logger
logger = logging.getLogger(__name__)

def remove_from_bag(request, artwork_id):
    """Remove the specified artwork from the shopping bag."""
    try:
        bag = request.session.get('bag', {})
        artwork = Artwork.objects.get(pk=artwork_id)
        logger.info("Bag contents before removal: %s", bag)

        if str(artwork_id) in bag:
            del bag[str(artwork_id)]
            messages.success(request, f'Removed "{artwork.title}" from your bag.')
            logger.info("Removed artwork ID %s from the bag.", artwork_id)
        else:
            logger.warning("Artwork ID %s not found in the bag.", artwork_id)
            messages.warning(request, f'Artwork "{artwork.title}" not found in your bag.')

        request.session['bag'] = bag
        logger.info("Bag contents after removal: %s", bag)
        return HttpResponse(status=200)

    except Exception as e:
        logger.error("Error while removing artwork ID %s: %s", artwork_id, e)
        messages.error(request, f'Error removing "{artwork.title}": {e}')
        return HttpResponse(status=500)
