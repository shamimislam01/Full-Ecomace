from django.db import models
from django.utils import timezone
from account.models import CustomUser

# Create your models here.


class SupportTicket(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='open')  # open, in_progress, closed
    priority = models.CharField(max_length=20, default='low')  # low, medium, high
    # Add any other fields you need, like attachments, etc.


    def __str__(self):
        return f"{self.subject} - {self.user.username}"
    
class SupportResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user who made the response

    def __str__(self):
        return f"Response to {self.ticket.subject} by {self.user.username}"
    

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.subject}"
    

class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)  # open, in_progress, closed
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user who changed the status

    def __str__(self):
        return f"Status change for {self.ticket.subject} to {self.status} by {self.changed_by.username}"
    

class TicketPriorityHistory(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='priority_history')
    priority = models.CharField(max_length=20)  # low, medium, high
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user who changed the priority

    def __str__(self):
        return f"Priority change for {self.ticket.subject} to {self.priority} by {self.changed_by.username}"
    
class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact Us from {self.name} - {self.subject}"

