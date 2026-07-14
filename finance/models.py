from django.db import models
from procurement.models import PurchaseOrder, GoodsReceiptNote

class Invoice(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE) #[cite: 1]
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.CASCADE) #[cite: 1]
    billed_amount = models.DecimalField(max_digits=10, decimal_places=2) #[cite: 1]
    is_paid = models.BooleanField(default=False) #[cite: 1]
