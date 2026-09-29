from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0048_remove_hospital_ambulances_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=[
                    ('identification', 'Patient Identification'),
                    ('status', 'Patient Status'),
                    ('contidion', 'Patient Condition'),
                    ('transfer', 'Patient Transfer'),
                    ('release', 'Patient Release'),
                    ('match', 'AI Match'),
                    ('fire_alert', 'Fire Alert'),
                ],
                max_length=50,
            ),
        ),
    ]