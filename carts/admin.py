from django.contrib import admin
from .models import  CartItem,Cart

# Register your models here.

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('added_at',)
    ordering = ('-added_at',)
    date_hierarchy = 'added_at'
    list_per_page = 20

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'added_at')
    search_fields = ('user__username',)
    list_filter = ('added_at',)
    ordering = ('-added_at',)
    date_hierarchy = 'added_at'
    list_per_page = 20



admin.site.register(CartItem )
admin.site.register(Cart)
