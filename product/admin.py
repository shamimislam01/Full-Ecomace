# admin.py
from django.contrib import admin
from .models import Product, ProductCategory, ProductReview

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'old_price','new_price', 'stock', 'is_active', 'is_discount_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    # prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('product', 'user', 'rating')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-created_at',)

