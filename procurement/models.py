from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import Item
from suppliers.models import Supplier

User = get_user_model()

class StoreRequisition(models.Model):
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('ISSUED', 'Issued'), ('DEMAND_ADDED', 'Demand Added')] #[cite: 1]
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE) #[cite: 1]
    item = models.ForeignKey(Item, on_delete=models.CASCADE) #[cite: 1]
    quantity = models.IntegerField() #[cite: 1]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT') #[cite: 1]

class Demand(models.Model):
    STATUS_CHOICES = [('PENDING_QUOTES', 'Pending Quotations'), ('CST_READY', 'CST Ready')] #[cite: 1]
    requisition = models.OneToOneField(StoreRequisition, on_delete=models.CASCADE) #[cite: 1]
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_QUOTES') #[cite: 1]

class Quotation(models.Model):
    demand = models.ForeignKey(Demand, on_delete=models.CASCADE, related_name='quotations') #[cite: 1]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE) #[cite: 1]
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) #[cite: 1]
    delivery_days = models.IntegerField() #[cite: 1]
    is_chosen = models.BooleanField(default=False) #[cite: 1]

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('PENDING_BUDGET', 'Pending Budget Approval'), ('PO_ISSUED', 'PO Issued'), ('DELIVERED', 'Delivered')] #[cite: 1]
    demand = models.OneToOneField(Demand, on_delete=models.CASCADE) #[cite: 1]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE) #[cite: 1]
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) #[cite: 1]
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_BUDGET') #[cite: 1]

class GoodsReceiptNote(models.Model):
    QAD_CHOICES = [
        ('PENDING', 'Temporary GRN'), ('RFR', 'Return for Replacement'), #[cite: 1]
        ('REJECT', 'Rejected to Vendor'), ('ACCEPT', 'Accepted to Store'), #[cite: 1]
        ('USER_ACCEPT', 'User Accepted'), ('CIT', 'Consume in Test') #[cite: 1]
    ]
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE) #[cite: 1]
    received_quantity = models.IntegerField() #[cite: 1]
    qad_status = models.CharField(max_length=20, choices=QAD_CHOICES, default='PENDING') #[cite: 1]
