[33mcommit a4cb76a8c2f101da81945668426c47f0eb70c1b6[m[33m ([m[1;36mHEAD -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m)[m
Author: rehansohan <rehansohan5303@gmail.com>
Date:   Fri Sep 4 21:36:13 2026 +0600

    Fix Render superuser creation

[1mdiff --git a/build.sh b/build.sh[m
[1mindex d1463fc..836375e 100644[m
[1m--- a/build.sh[m
[1m+++ b/build.sh[m
[36m@@ -1,80 +1,80 @@[m
[31m-#!/usr/bin/env bash[m
[31m-[m
[31m-set -e[m
[31m-[m
[31m-echo "========================================"[m
[31m-echo "Installing dependencies..."[m
[31m-echo "========================================"[m
[31m-[m
[31m-pip install -r requirements.txt[m
[31m-[m
[31m-[m
[31m-echo "========================================"[m
[31m-echo "Running database migrations..."[m
[31m-echo "========================================"[m
[31m-[m
[31m-python manage.py migrate --noinput[m
[31m-[m
[31m-[m
[31m-echo "========================================"[m
[31m-echo "Creating/updating superuser..."[m
[31m-echo "========================================"[m
[31m-[m
[31m-python manage.py shell -c "[m
[31m-import os[m
[31m-from django.contrib.auth import get_user_model[m
[31m-[m
[31m-User = get_user_model()[m
[31m-[m
[31m-username = os.environ.get('DJANGO_SUPERUSER_USERNAME')[m
[31m-email = os.environ.get('DJANGO_SUPERUSER_EMAIL')[m
[31m-password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')[m
[31m-[m
[31m-print('----------------------------------------')[m
[31m-print('Superuser configuration')[m
[31m-print('Username:', username)[m
[31m-print('Email:', email)[m
[31m-print('----------------------------------------')[m
[31m-[m
[31m-if not username or not password:[m
[31m-    print('ERROR: Superuser environment variables are missing!')[m
[31m-    raise SystemExit(1)[m
[31m-[m
[31m-user, created = User.objects.get_or_create([m
[31m-    username=username[m
[31m-)[m
[31m-[m
[31m-user.email = email or user.email[m
[31m-user.set_password(password)[m
[31m-user.is_staff = True[m
[31m-user.is_superuser = True[m
[31m-user.is_active = True[m
[31m-user.save()[m
[31m-[m
[31m-print('Superuser created:', created)[m
[31m-print('Superuser username:', user.username)[m
[31m-print('Staff:', user.is_staff)[m
[31m-print('Superuser:', user.is_superuser)[m
[31m-print('Active:', user.is_active)[m
[31m-[m
[31m-if user.check_password(password):[m
[31m-    print('Password check: True')[m
[31m-    print('Superuser is ready!')[m
[31m-else:[m
[31m-    print('Password check: False')[m
[31m-    print('ERROR: Password verification failed!')[m
[31m-    raise SystemExit(1)[m
[31m-[m
[31m-"[m
[31m-[m
[31m-[m
[31m-echo "========================================"[m
[31m-echo "Collecting static files..."[m
[31m-echo "========================================"[m
[31m-[m
[31m-python manage.py collectstatic --noinput[m
[31m-[m
[31m-[m
[31m-echo "========================================"[m
[31m-echo "Build completed successfully."[m
[32m+[m[32m#!/usr/bin/env bash[m
[32m+[m
[32m+[m[32mset -e[m
[32m+[m
[32m+[m[32mecho "========================================"[m
[32m+[m[32mecho "Installing dependencies..."[m
[32m+[m[32mecho "========================================"[m
[32m+[m
[32m+[m[32mpip install -r requirements.txt[m
[32m+[m
[32m+[m
[32m+[m[32mecho "========================================"[m
[32m+[m[32mecho "Running database migrations..."[m
[32m+[m[32mecho "========================================"[m
[32m+[m
[32m+[m[32mpython manage.py migrate --noinput[m
[32m+[m
[32m+[m
[32m+[m[32mecho "========================================"[m
[32m+[m[32mecho "Creating/updating superuser..."[m
[32m+[m[32mecho "========================================"[m
[32m+[m
[32m+[m[32mpython manage.py shell -c "[m
[32m+[m[32mimport os[m
[32m+[m[32mfrom django.contrib.auth import get_user_model[m
[32m+[m
[32m+[m[32mUser = get_user_model()[m
[32m+[m
[32m+[m[32musername = os.environ.get('DJANGO_SUPERUSER_USERNAME')[m
[32m+[m[32memail = os.environ.get('DJANGO_SUPERUSER_EMAIL')[m
[32m+[m[32mpassword = os.environ.get('DJANGO_SUPERUSER_PASSWORD')[m
[32m+[m
[32m+[m[32mprint('----------------------------------------')[m
[32m+[m[32mprint('Superuser configuration')[m
[32m+[m[32mprint('Username:', username)[m
[32m+[m[32mprint('Email:', email)[m
[32m+[m[32mprint('----------------------------------------')[m
[32m+[m
[32m+[m[32mif not username or not password:[m
[32m+[m[32m    print('ERROR: Superuser environment variables are missing!')[m
[32m+[m[32m    raise SystemExit(1)[m
[32m+[m
[32m+[m[32muser, created = User.objects.get_or_create([m
[32m+[m[32m    username=username[m
[32m+[m[32m)[m
[32m+[m
[32m+[m[32muser.email = email or user.email[m
[32m+[m[32muser.set_password(password)[m
[32m+[m[32muser.is_staff = True[m
[32m+[m[32muser.is_superuser = True[m
[32m+[m[32muser.is_active = True[m
[32m+[m[32muser.save()[m
[32m+[m
[32m+[m[32mprint('Superuser created:', created)[m
[32m+[m[32mprint('Superuser username:', user.username)[m
[32m+[m[32mprint('Staff:', user.is_staff)[m
[32m+[m[32mprint('Superuser:', user.is_superuser)[m
[32m+[m[32mprint('Active:', user.is_active)[m
[32m+[m
[32m+[m[32mif user.check_password(password):[m
[32m+[m[32m    print('Password check: True')[m
[32m+[m[32m    print('Superuser is ready!')[m
[32m+[m[32melse:[m
[32m+[m[32m    print('Password check: False')[m
[32m+[m[32m    print('ERROR: Password verification failed!')[m
[32m+[m[32m    raise SystemExit(1)[m
[32m+[m
[32m+[m[32m"[m
[32m+[m
[32m+[m
[32m+[m[32mecho "========================================"[m
[32m+[m[32mecho "Collecting static files..."[m
[32m+[m[32mecho "========================================"[m
[32m+[m
[32m+[m[32mpython manage.py collectstatic --noinput[m
[32m+[m
[32m+[m
[32m+[m[32mecho "========================================"[m
[32m+[m[32mecho "Build completed successfully."[m
 echo "========================================"[m
\ No newline at end of file[m
