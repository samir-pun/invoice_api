from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client_name', 'status', 'subtotal', 'tax', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'client_name', 'client_email')

    inlines = [InvoiceItemInline]

    readonly_fields = ('subtotal', 'tax', 'total')





@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price')   