#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import execute_from_command_line

execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])

print("Build completed successfully!")
