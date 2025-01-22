from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''


register = template.Library()

@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    """
    Calculate the subtotal for an artwork based on its price and quantity.
    """
    return price * quantity

