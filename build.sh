#!/usr/bin/env bash

set -e

echo "========================================"
echo "Installing dependencies..."
echo "========================================"

pip install -r requirements.txt


echo "========================================"
echo "Running database migrations..."
echo "========================================"

python manage.py migrate --noinput


echo "========================================"
echo "Creating/updating superuser..."
echo "========================================"

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

print('----------------------------------------')
print('Superuser configuration')
print('Username:', username)
print('Email:', email)
print('----------------------------------------')

if not username or not password:
    print('ERROR: Superuser environment variables are missing!')
    raise SystemExit(1)

user, created = User.objects.get_or_create(
    username=username
)

user.email = email or user.email
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

print('Superuser created:', created)
print('Superuser username:', user.username)
print('Staff:', user.is_staff)
print('Superuser:', user.is_superuser)
print('Active:', user.is_active)

if user.check_password(password):
    print('Password check: True')
    print('Superuser is ready!')
else:
    print('Password check: False')
    print('ERROR: Password verification failed!')
    raise SystemExit(1)

"


echo "========================================"
echo "Collecting static files..."
echo "========================================"

python manage.py collectstatic --noinput


echo "========================================"
echo "Build completed successfully."
echo "========================================"