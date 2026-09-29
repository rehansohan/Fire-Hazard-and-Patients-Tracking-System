from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0049_notification_fire_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='identified_by_users',
            field=models.ManyToManyField(
                blank=True,
                related_name='identified_patients_by',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]