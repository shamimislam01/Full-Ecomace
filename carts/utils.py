# carts/utils.py

def calculate_cart_totals(cart):
    cart_items = cart.items.all()
    subtotal = sum(item.product.new_price * item.quantity for item in cart_items)

    if cart_items.exists():
        shipping = 120
        discount = 10
    else:
        shipping = 0
        discount = 0

    final_total = subtotal + shipping - discount

    # প্রতিটি আইটেমে total_price যোগ করা
    for item in cart_items:
        item.total_price = item.product.new_price * item.quantity

    return {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'discount': discount,
        'final_total': final_total
    }
