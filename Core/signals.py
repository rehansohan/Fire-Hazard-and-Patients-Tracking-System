from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Patient
from .utils.auto_match import run_ai_matching


@receiver(post_save,sender=Patient)
def patient_saved(sender,instance,created, **kwarges):
    """
    Automatically run AI matching when a new patient is added.
    """
    if created:
        run_ai_matching(instance)
        
        


from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Patient, Notification


@receiver(pre_save, sender=Patient)
def patient_pre_save(sender, instance, **kwargs):

    """
    Store the previous patient information before update.
    """

    if not instance.pk:
        instance._old_patient = None
        return

    try:
        instance._old_patient = Patient.objects.get(
            pk=instance.pk
        )
    except Patient.DoesNotExist:
        instance._old_patient = None


@receiver(post_save, sender=Patient)
def patient_post_save(
    sender,
    instance,
    created,
    **kwargs
):

    """
    Create notifications when an identified patient's
    important information changes.
    """

    # Don't notify for a brand-new patient
    if created:
        return

    # Patient must be identified
    if not instance.is_identified:
        return

    # A user must be associated with the patient
    if not instance.identified_by:
        return

    old_patient = getattr(
        instance,
        '_old_patient',
        None
    )

    if not old_patient:
        return

    notifications = []

    # --------------------------------
    # STATUS CHANGED
    # --------------------------------

    if old_patient.status != instance.status:

        # Special message for release
        if instance.status == 'released':

            title = 'Patient Released'

            message = (
                f'Patient {instance.patient_id} '
                f'has been released from the hospital.'
            )

            notification_type = 'release'

        # Special message for transfer
        elif instance.status == 'transferred':

            title = 'Patient Transferred'

            message = (
                f'Patient {instance.patient_id} '
                f'has been transferred to another hospital.'
            )

            notification_type = 'transfer'

        else:

            title = 'Patient Status Updated'

            message = (
                f'Patient {instance.patient_id} status changed '
                f'from {old_patient.status} to {instance.status}.'
            )

            notification_type = 'status'

        notifications.append(
            Notification(
                user=instance.identified_by,
                patient=instance,
                title=title,
                message=message,
                notification_type=notification_type
            )
        )

    # --------------------------------
    # CONDITION CHANGED
    # --------------------------------

    if old_patient.condition != instance.condition:

        notifications.append(
            Notification(
                user=instance.identified_by,
                patient=instance,
                title='Patient Condition Updated',
                message=(
                    f'The condition of patient '
                    f'{instance.patient_id} has changed '
                    f'from {old_patient.condition} '
                    f'to {instance.condition}.'
                ),
                notification_type='condition'
            )
        )

    # --------------------------------
    # HOSPITAL CHANGED
    # --------------------------------

    if old_patient.hospital_id != instance.hospital_id:

        notifications.append(
            Notification(
                user=instance.identified_by,
                patient=instance,
                title='Patient Hospital Updated',
                message=(
                    f'Patient {instance.patient_id} '
                    f'has been transferred to another hospital.'
                ),
                notification_type='transfer'
            )
        )

    # --------------------------------
    # CREATE NOTIFICATIONS
    # --------------------------------

    if notifications:

        Notification.objects.bulk_create(
            notifications
        )
        

