from django.contrib.auth.models import Group

class ApprovalRule(models.Model):
    """
    Stores dynamic routing rules for financial thresholds.
    """
    rule_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50, default='PO') # e.g., PO, INVOICE
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Links to standard Django auth Groups (e.g., 'Manager', 'Director', 'CEO')
    required_group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        db_table = 'procurement_approval_rules'

class ApprovalRecord(models.Model):
    """
    Tracks the actual approval lifecycle of a specific document (like a PO).
    """
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.CASCADE, related_name='approvals')
    rule_applied = models.ForeignKey(ApprovalRule, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')],
        default='PENDING'
    )
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'procurement_approval_records'
