from django import template
from carts.models import CartItem

register = template.Library()

@register.filter
def get_item(item_total_prices, item_id):
    try:
        # Ensure that item_total_prices is a dictionary or similar structure
        item = CartItem.objects.get(id=item_id)
        return item.product.new_price * item.quantity
    except CartItem.DoesNotExist:
        return 0  # or some fallback value
