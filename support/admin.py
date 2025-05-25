from django.contrib import admin
from .models import SupportTicket, SupportResponse, TicketAttachment, TicketStatusHistory, TicketPriorityHistory, ContactUs

# Register your models here.

class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'priority', 'created_at')
    search_fields = ('subject', 'user__username')
    list_filter = ('status', 'priority')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20

class SupportResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'created_at')
    search_fields = ('ticket__subject', 'user__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20


class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'uploaded_at')
    search_fields = ('ticket__subject',)
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'
    list_per_page = 20

class TicketStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'status', 'changed_at', 'changed_by')
    search_fields = ('ticket__subject', 'changed_by__username')
    ordering = ('-changed_at',)
    date_hierarchy = 'changed_at'
    list_per_page = 20

class TicketPriorityHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'priority', 'changed_at', 'changed_by')
    search_fields = ('ticket__subject', 'changed_by__username')
    ordering = ('-changed_at',)
    date_hierarchy = 'changed_at'
    list_per_page = 20

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20

admin.site.register(SupportTicket, SupportTicketAdmin)
admin.site.register(SupportResponse, SupportResponseAdmin)
admin.site.register(TicketAttachment, TicketAttachmentAdmin)
admin.site.register(TicketStatusHistory, TicketStatusHistoryAdmin)
admin.site.register(TicketPriorityHistory, TicketPriorityHistoryAdmin)
admin.site.register(ContactUs, ContactUsAdmin)


