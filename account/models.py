from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_token = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)

    address_line_1 = models.CharField(null=True, blank=True, max_length=100)
    address_line_2 = models.CharField(null=True, blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=20)
    postcode = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    mobile = models.CharField(null=True, blank=True, max_length=15)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="user_profile")

    USERNAME_FIELD = 'username'      # লগইনে মূল ফিল্ড হিসেবে username থাকবে
    REQUIRED_FIELDS = ['email']      # createsuperuser এর সময় email চাইবে

    def full_address(self):
        return f"{self.address_line_1 or ''} {self.address_line_2 or ''}"
    


class EmailOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"
    
    def is_expired(self):
        """Check if the OTP is expired (5 minutes limit)."""
        return timezone.now() - self.created_at > timezone.timedelta(minutes=5)
    







