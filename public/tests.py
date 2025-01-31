from django.test import TestCase
from . models import Tenant, Domain
from decouple import config
from django_tenants.utils import schema_context
from django.contrib.auth.models import User
from base.messages import sendmail
from publicuser.models import PublicUser

# Create your tests here.

def create():
    try:

        tenant = Tenant(schema_name='public', name='Public', is_active=True, is_master=True)
        tenant.save()
        print('Connected Tenant with "public"')
        domain_obj = Domain(domain='localhost', tenant=tenant, is_primary=True)
        domain_obj.save()
        print('Created Domain for "public"')
    except Exception as e:
        print(e)

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
                get_or_create_publicuser(user_obj)
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
                get_or_create_publicuser(user_obj)

def get_or_create_publicuser(user_obj):
    publicuser = PublicUser.objects.filter(user=user_obj).first()
    if publicuser:
        print('Public User already exists')
    else:
        publicuser, created_publicuser = PublicUser.objects.get_or_create(
            user=user_obj
        )
        if created_publicuser:
            print('Public User created!')
        else:
            print('Public User already exists.')