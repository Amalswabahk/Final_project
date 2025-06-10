


# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        User.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Payment, PaymentHistory

@receiver(pre_save, sender=Payment)
def track_payment_changes(sender, instance, **kwargs):
    if instance.pk:  # Only for existing instances
        try:
            original = Payment.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Payment.DoesNotExist:
            pass

@receiver(post_save, sender=Payment)
def create_payment_history(sender, instance, created, **kwargs):
    if created:
        PaymentHistory.objects.create(
            payment=instance,
            status=instance.status,
            changed_by=instance.created_by,
            notes="Initial payment creation",
            metadata={
                'amount': float(instance.amount),
                'method': instance.payment_method
            }
        )
    else:
        if hasattr(instance, '_original_status') and instance._original_status != instance.status:
            PaymentHistory.objects.create(
                payment=instance,
                status=instance.status,
                changed_by=instance.created_by,
                notes=f"Status changed from {instance._original_status} to {instance.status}",
                metadata={
                    'previous_status': instance._original_status,
                    'new_status': instance.status,
                    'changed_fields': {
                        'status': {
                            'from': instance._original_status,
                            'to': instance.status
                        }
                    }
                }
            )