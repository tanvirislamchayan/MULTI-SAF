from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

# Create your models here.

class Tenant(TenantMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_master = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)
    favicon = models.ImageField(upload_to='user_favicons/')


class Domain(DomainMixin):
    pass
