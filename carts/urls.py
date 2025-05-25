from django.urls import path

from . import views


urlpatterns = [

    path('', views.cart_view, name='cart'),
    # path('update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),    
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-quantity/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('checkout/', views.checkout_view, name='checkout'),  # 'checkout' প্যাটার্ন
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed_view, name='payment_failed'),
    
    # path('add-cart/', views.add_cart, name='add_cart'),

    # path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    # path('pluscart/', views.plus_cart, name='plus_cart'),

]
