from django.test import TestCase
from . models import Tenant, Domain
from decouple import config
from django_tenants.utils import schema_context
from django.contrib.auth.models import User
from base.messages import sendmail

# Create your tests here.

def create():
    tenant = Tenant(schema_name='public', name='Public', is_active=True, is_master=True)
    tenant.save()
    print('Connected Tenant with "public"')
    domain_obj = Domain(domain='localhost', tenant=tenant, is_primary=True)
    domain_obj.save()
    print('Created Domain for "public"')

    # create public user
    users = {
        'user_1': {
            'first_name': 'Tanvir',
            'last_name': 'Islam',
            'email': config('USER_1_EMAIL'),
            'password': config('USER_1_PASS')
        },
        'user_2': {
            'first_name': 'Engr. Manik',
            'last_name': 'Ullah',
            'email': config('USER_2_EMAIL'),
            'password': config('USER_2_PASS')
        },
        'user_3': {
            'first_name': 'Muslima',
            'last_name': 'Jahan',
            'email': config('USER_3_EMAIL'),
            'password': config('USER_3_PASS')
        },
    }

    with schema_context('public'):
        for user, user_data in users.items():
            user_obj, created = User.objects.get_or_create(
                username = user_data['email'],
                defaults={
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'email': user_data.get('email', ''),
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                }
            )
            if created:
                user_obj.set_password(user_data.get('password', ''))
                user_obj.save()
                context = {
                    'name': f'{user_obj.first_name} {user_obj.last_name}',
                    'username': user_obj.email,
                    'message': 'Your account has been successfully created on the SAF domain. \n'
                        'You can now log in and start using our services.',
                    'domain': domain_obj.domain, 
                    'password': user_data.get('password', '')
                }
                sendmail(
                    recipient_name=user_obj.email,  # Individual email as a string
                    message=None, 
                    subject="Welcome to SAF Domain",  # Add a meaningful subject
                    recipient_email=[user_obj.email],  # Pass the email in a list
                    template_name='superuser.html', 
                    domain=domain_obj.domain,  # Pass the domain if needed in the email template
                    context=context
                )
                print(f'User created for {user_obj.first_name} {user_obj.last_name}')
            else:
                print('User already exists.')