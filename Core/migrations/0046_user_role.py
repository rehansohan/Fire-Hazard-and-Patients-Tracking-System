from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('Core', '0045_user_blood_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrator'),
                    ('hospital_staff', 'Hospital Staff'),
                    ('volunteer', 'Volunteer'),
                    ('user', 'General User'),
                ],
                default='user',
                max_length=30,
            ),
        ),
    ]
