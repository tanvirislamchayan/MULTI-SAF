from django.db import models
from base.models import BaseModel
from public.models import Tenant
from django.contrib.auth.models import User

# Create your models here.

class TenantUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    is_subadmin = models.BooleanField(default=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)