from django import template

register = template.Library()

@register.filter
def calculate_subtotal(cart_item, currency_preference):
    return cart_item.subtotal(currency_preference)