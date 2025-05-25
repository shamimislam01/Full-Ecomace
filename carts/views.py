from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import CartItem, Cart
from product.models import Product
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST ,require_GET
from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order, OrderAddress, OrderItem
from .utils import calculate_cart_totals
# from sslcommerz_python_api import SSLCSession
from sslcommerz_lib import SSLCOMMERZ
from django.db import transaction


from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from orders.models import Payment



@login_required
def cart_view(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, is_guest=False)
    else:
        # Guest user logic (same as before)
        session_cart_id = request.session.get('cart_id', None)
        if not session_cart_id:
            cart = Cart.objects.create(is_guest=True)
            request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.get(id=session_cart_id)

    totals = calculate_cart_totals(cart)

    return render(request, 'cart.html', {
        'cart': cart,
        **totals
    })









# Update the quantity of items in the cart
@login_required
def update_quantity(request, item_id, action):
   
    cart = get_object_or_404(Cart, user=request.user, is_guest=False)

    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Quantity increased successfully.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, "Quantity decreased successfully.")
        else:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")

    return redirect('cart')



# Remove an item from the cart
@require_POST
def remove_cart_item(request, item_id):
    try:
        # Try to get the cart item
        item = CartItem.objects.get(id=item_id)
        item.delete()  # Remove the item
        
        # After successful removal, display a success message
        messages.success(request, "Item removed from cart successfully.")

        # If it's an AJAX request, return JSON response with updated cart data
        if request.is_ajax():
            cart = Cart.objects.get(user=request.user) if request.user.is_authenticated else Cart.objects.get(id=request.session['cart_id'])
            cart_items = CartItem.objects.filter(cart=cart)
            total_price = sum([item.product.new_price * item.quantity if item.product.is_discount_active else item.product.old_price * item.quantity for item in cart_items])
            final_total = total_price - 26 + 5  # Discount and shipping included
            
            return JsonResponse({
                'status': 'success',
                'message': 'Item removed',
                'cart_items_count': cart_items.count(),
                'total_price': total_price,
                'final_total': final_total
            })
        
    except CartItem.DoesNotExist:
        # If item does not exist, display an error message
        messages.error(request, "Item not found in cart.")
        return JsonResponse({'status': 'error', 'message': 'Item not found'})

    return redirect('cart')





@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user, is_guest=False)

    # Quantity frontend থেকে নেওয়া
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    # Check if item already in cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
     
        cart_item.quantity += quantity
        messages.success(request, f"{product.name} quantity updated in cart.")
    else:
        cart_item.quantity = quantity
        messages.success(request, f"{product.name} added to cart.")

    cart_item.save()

    return redirect('cart')




@login_required
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.cart.user != request.user:
        messages.error(request, "You don't have permission to delete this item.")
        return redirect('cart')

    cart_item.delete()
    messages.success(request, "Item removed from cart successfully.")
    return redirect('cart')



@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user, is_guest=False)
    totals = calculate_cart_totals(cart)

    if request.method == 'POST':
        address_option = request.POST.get('address_option')
        payment_method = request.POST.get('payment_method')

        if payment_method not in ['cod', 'bkash', 'nagad', 'sslcommerz']:
            messages.error(request, "Invalid payment method selected.")
            return redirect('checkout')

        
        if address_option == 'profile':
            phone = request.user.mobile
            if not phone:
                messages.error(request, "Your profile is missing a phone number. Please complete your profile first.")
                return redirect('dashboard')
            address = OrderAddress(
                full_name=request.user.get_full_name(),
                phone=phone,
                address=request.user.address_line_1,
                city=request.user.city,
                zip_code=request.user.postcode,
                use_profile_address=True
            )
        else:
            address = OrderAddress(
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                zip_code=request.POST.get('zip_code'),
                use_profile_address=False
            )

        with transaction.atomic():
            # ✅ Order তৈরি কর
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                total_price=totals['final_total'],
                payment_method=payment_method,
                is_paid=False
            )

            address.order = order
            address.save()

            for item in cart.items.select_related('product').all():
                # ✅ Stock কমাও
                product = item.product
                if product.stock < item.quantity:
                   messages.error(request, f"'{product.name}' এর যথেষ্ট স্টক নেই!")
                   return redirect('checkout')  # অথবা যেখানে তুই checkout page দেখাস


                product.stock -= item.quantity
                product.save()

                # ✅ OrderItem তৈরি কর
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.new_price
                )

            if payment_method == 'sslcommerz':
                # ✅ SSLCOMMERZ init
                settings_data = {
                    'store_id': settings.SSLCOMMERZ_STORE_ID,
                    'store_pass': settings.SSLCOMMERZ_API_KEY,
                    'issandbox': True  # ⚠️ Live হলে False কর
                }
                sslcz = SSLCOMMERZ(settings_data)

                post_body = {
                    'total_amount': str(totals['final_total']),
                    'currency': "BDT",
                    'tran_id': f"ORDER_{order.id}",
                    'success_url': request.build_absolute_uri(reverse('payment_success')),
                    'fail_url': request.build_absolute_uri(reverse('payment_failed')),
                    'cancel_url': request.build_absolute_uri(reverse('checkout')),
                    'emi_option': 0,
                    'cus_name': address.full_name,
                    'cus_email': request.user.email or "dummy@email.com",
                    'cus_phone': address.phone,
                    'cus_add1': address.address,
                    'cus_city': address.city,
                    'cus_postcode': address.zip_code,
                    'cus_country': "Bangladesh",
                    'shipping_method': "NO",
                    'product_name': "Ecommerce Order",
                    'product_category': "Mixed",
                    'product_profile': "general"
                }

                response = sslcz.createSession(post_body)

                if response.get('status') == 'SUCCESS':
                    return redirect(response['GatewayPageURL'])
                else:
                    messages.error(request, "SSLCOMMERZ session failed.")
                    return redirect('checkout')

            # ✅ COD, Bkash, Nagad হলে
            cart.items.all().delete()
        
        messages.success(request, "Order placed successfully.")
        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'user': request.user,
        'cart': cart,
        **totals
    })







@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = request.POST
        tran_id = data.get('tran_id')  # e.g., ORDER_23

        if not tran_id or not tran_id.startswith("ORDER_"):
            return HttpResponse("Invalid transaction ID", status=400)

        try:
            order_id = int(tran_id.split("_")[1])
            order = Order.objects.get(id=order_id)
        except (ValueError, Order.DoesNotExist):
            return HttpResponse("Order not found", status=404)

        user = order.user  # ✅ ইউজার এখানে থেকে পাওয়া যাবে

        status = data.get('status')
        if status == 'VALID':
            order.is_paid = True
            order.status = 'processing'
            order.save()

            Payment.objects.create(
                user=user,
                order=order,
                transaction_id=data.get('val_id'),
                amount=order.total_price,
                status='SUCCESS',
                payment_method='sslcommerz',
                validation_data=data.dict()
            )

            # ✅ ক্যার্ট এবং আইটেম মুছে ফেল
            try:
                cart = Cart.objects.get(user=user, is_guest=False)
                cart.delete()
            except Cart.DoesNotExist:
                pass

            # ✅ success page এ redirect
            return redirect('order_success', order_id=order.id)

        else:
            Payment.objects.create(
                user=user,
                order=order,
                transaction_id=data.get('val_id') or tran_id,
                amount=order.total_price,
                status='FAILED',
                payment_method='sslcommerz',
                validation_data=data.dict()
            )
            return HttpResponse("Payment failed", status=400)

    return HttpResponse("Invalid request", status=400)






@login_required
@csrf_exempt
def payment_failed(request):
    messages.error(request, "Payment failed or was cancelled.")
    return redirect('checkout')






@login_required
def order_success(request,order_id):

    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # অর্ডার সংখ্যা গোনা
    total_orders = orders.count()
    pending_orders = orders.filter(order_status='pending').count()
    delivered_orders = orders.filter(order_status='delivered').count()
    in_transit_orders = orders.filter(order_status='shipped').count() + orders.filter(order_status='processing').count()
    order = get_object_or_404(Order, id=order_id, user=user)

    recent_orders = orders[:5]  # সর্বশেষ ৫টি অর্ডার দেখানো হবে

    context = {
        'order': order,
        'user': user,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'in_transit_orders': in_transit_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'success.html', context)



def payment_failed_view(request):
    return render(request, 'payment_failed.html')