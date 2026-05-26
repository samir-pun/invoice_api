from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    client_name = models.CharField(max_length=255)
    client_email = models.EmailField(blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)

    invoice_number = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(default=timezone.now)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    TAX_RATE = Decimal("0.13")

    def calculate_totals(self):
        items = self.items.all()

        subtotal = sum(item.quantity * item.unit_price for item in items)
        subtotal = Decimal(subtotal)

        tax = subtotal * self.TAX_RATE
        total = subtotal + tax

        # ⚠️ IMPORTANT: NO save() here
        self.subtotal = subtotal
        self.tax = tax
        self.total = total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def get_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description


# 🔥 SAFE SIGNALS (NO LOOP)

@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def update_invoice_totals(sender, instance, **kwargs):
    invoice = instance.invoice
    if invoice:
        invoice.calculate_totals()
        invoice.save(update_fields=["subtotal", "tax", "total"])