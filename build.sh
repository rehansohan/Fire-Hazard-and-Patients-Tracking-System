python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email or '',
            'is_staff': True,
            'is_superuser': True,
        }
    )

    user.email = email or user.email
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    if created:
        print('Superuser created successfully.')
    else:
        print('Superuser password updated successfully.')
"
