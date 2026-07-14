from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from documents.models import Document
from procurement.models import PurchaseOrder
from .models import AuditLog

@receiver(pre_save, sender=PurchaseOrder)
@receiver(pre_save, sender=Document)
def capture_old_values(sender, instance, **kwargs):
    """Stores the old state of the object before it is saved."""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_state = {
                field.name: getattr(old_instance, field.name) 
                for field in sender._meta.fields
            }
        except sender.DoesNotExist:
            instance._old_state = {}
    else:
        instance._old_state = {}

@receiver(post_save, sender=PurchaseOrder)
@receiver(post_save, sender=Document)
def log_changes(sender, instance, created, **kwargs):
    """Compares old state to new state and writes to the AuditLog."""
    action = 'CREATE' if created else 'UPDATE'
    changes = {}

    if not created and hasattr(instance, '_old_state'):
        for field in sender._meta.fields:
            old_val = instance._old_state.get(field.name)
            new_val = getattr(instance, field.name)
            if old_val != new_val:
                changes[field.name] = [str(old_val), str(new_val)]

    # Only log updates if something actually changed
    if created or changes:
        AuditLog.objects.create(
            action=action,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
            changes=changes
        )
