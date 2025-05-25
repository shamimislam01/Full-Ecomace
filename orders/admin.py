from django.contrib import admin
from .models import Order, OrderAddress, OrderItem, Payment

class OrderAddressInline(admin.StackedInline):
    model = OrderAddress
    extra = 0
    can_delete = False


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderAddressInline,PaymentInline]
    list_display = ['id', 'order_number', 'user', 'total_price', 'is_paid', 'created_at']
    list_filter = ['is_paid', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderAddress)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price']
    list_filter = ['order', 'product']
    search_fields = ['order__order_number', 'product__name']

admin.site.register(OrderItem, OrderItemAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order', 'transaction_id', 'amount', 'created_at']
    list_filter = ['user', 'order']
    search_fields = ['transaction_id', 'user__username', 'order__order_number']

admin.site.register(Payment, PaymentAdmin)
