from django.test import TestCase
from . models import Tenant, Domain

# Create your tests here.

def create():
    tenant = Tenant(schema_name='public', name='Public', is_active=True, is_master=True)
    tenant.save()
    domain = Domain(domain='localhost', tenant=tenant, is_primary=True)
    domain.save()