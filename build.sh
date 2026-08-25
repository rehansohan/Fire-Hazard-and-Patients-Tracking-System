#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py migrate

python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email or '',
            password=password
        )
        print('Superuser created successfully.')
    else:
        print('Superuser already exists.')
"

python manage.py collectstatic --noinput
