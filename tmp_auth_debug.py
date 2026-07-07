import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from django.contrib.auth import get_user_model, authenticate
User = get_user_model()
print('USERNAME_FIELD:', User.USERNAME_FIELD)
print('AUTH_USER_MODEL:', os.environ.get('DJANGO_SETTINGS_MODULE'))

# create or get a test user
user, created = User.objects.get_or_create(email='authtest@example.com', defaults={'username': 'authtest'})
if created:
    user.set_password('Password123')
    user.save()
    print('created test user')
else:
    print('user existed:', user.email, user.username)

print('email filter exists:', User.objects.filter(email='authtest@example.com').exists())
print('check password:', user.check_password('Password123'))
print('authenticate email:', authenticate(email='authtest@example.com', password='Password123'))
print('authenticate username:', authenticate(username='authtest', password='Password123'))
print('all usernames:', list(User.objects.filter(email='authtest@example.com').values('username','email')))
