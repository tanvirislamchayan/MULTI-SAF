from django.db import models
from django.core.validators import RegexValidator
from base.models import BaseModel
from django.contrib.auth.models import User
from public.models import Tenant

class PublicUser(BaseModel):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name='public_user')
    is_subadmin = models.BooleanField(default=False)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d{11}$', message="Phone number must be minimum 11 digits.")],
        help_text="Enter a valid phone number (e.g., +8801306609391).",
        null=True,
        blank=True,
    )
    institute = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username if self.user else "PublicUser"
    
