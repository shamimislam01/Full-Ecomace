from django.shortcuts import render
from .models import SupportTicket, SupportResponse, TicketAttachment, TicketStatusHistory, TicketPriorityHistory, ContactUs
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages



# Create your views here.

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Save the contact form data to the database
        contact_us = ContactUs(name=name, email=email, subject=subject, message=message)
        contact_us.save()
        messages.success(request, "Your message has been sent successfully!")


        
    return render(request, 'contact_from.html')
