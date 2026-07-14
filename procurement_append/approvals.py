from decimal import Decimal
from .models import PurchaseOrder, ApprovalRule, ApprovalRecord
import logging

logger = logging.getLogger(__name__)

class ApprovalService:
    
    @staticmethod
    def route_for_approval(po: PurchaseOrder):
        """
        Evaluates the PO amount against dynamic rules and creates an ApprovalRecord.
        """
        amount = po.total_amount
        
        # Find the rule where the amount falls between min and max
        # If max_amount is null, it acts as an upper bound (e.g., > $100,000)
        rule = ApprovalRule.objects.filter(
            document_type='PO',
            min_amount__lte=amount
        ).filter(
            models.Q(max_amount__gte=amount) | models.Q(max_amount__isnull=True)
        ).order_by('-min_amount').first()

        if rule:
            ApprovalRecord.objects.create(
                purchase_order=po,
                rule_applied=rule,
                status='PENDING'
            )
            logger.info(f"PO #{po.id} routed to {rule.required_group.name} for approval.")
            # Here you could trigger a Celery task to email the required_group
        else:
            # If no rules apply, auto-approve or fallback to a default state
            po.status = 'PO_ISSUED'
            po.save()
            logger.info(f"PO #{po.id} auto-issued. No approval rules matched.")
