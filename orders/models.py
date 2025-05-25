# orders/models.py

from django.db import models
from django.conf import settings
from carts.models import Cart
import uuid
from product.models import Product
from account.models import CustomUser

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('SSLCOMMERZ ', 'SSLCOMMERZ '),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
    ]

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)

    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    is_paid = models.BooleanField(default=False)

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    tracking_number = models.CharField(max_length=30, unique=True, null=True, blank=True)

    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    is_shipped = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(uuid.uuid4()).replace('-', '').upper()[:12]  # Auto-generate unique order number
        super().save(*args, **kwargs)
    def get_order_status_display(self):
        return dict(self.ORDER_STATUS_CHOICES).get(self.order_status, 'Unknown Status')
    

class OrderAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    use_profile_address = models.BooleanField(default=False)

    def __str__(self):
        return f"Shipping Address for Order #{self.order.id}"
    



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # সেফ করার সময় প্রাইস সেভ করে নিবি

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price
    



# models.py



class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # eg: SUCCESS, FAILED, CANCEL
    payment_method = models.CharField(max_length=20, default='sslcommerz')
    validation_data = models.JSONField(blank=True, null=True)  # raw response from SSLCOMMERZ
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} - {self.transaction_id}"



