# carts/models.py

from django.db import models
from account.models import CustomUser  # ইউজার মডেল যেখানে আছে
from product.models import Product  # প্রোডাক্ট মডেল যেখানে আছে

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # user optional for guest
    cart = models.ForeignKey('Cart', related_name='items', on_delete=models.CASCADE)  # Linking cart with CartItem
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.product.new_price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    is_guest = models.BooleanField(default=False)  # guest user indication
    added_at = models.DateTimeField(auto_now_add=True)

    def get_subtotal(self):
        return sum(item.subtotal() for item in self.items.all())  # Correct method name

    def get_total(self):
        return self.get_subtotal() + 5  # Shipping cost

    def __str__(self):
        return f"Cart of {self.user if self.user else 'Guest'}"
