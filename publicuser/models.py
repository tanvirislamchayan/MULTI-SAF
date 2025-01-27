from django.db import models, connection, transaction
from django.core.validators import RegexValidator
from base.models import BaseModel
from django.contrib.auth.models import User
from django_tenants.utils import schema_context, schema_exists, get_tenant_model
from public.models import Tenant, Domain
import logging

logger = logging.getLogger(__name__)

class PublicUser(BaseModel):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name='public_user')
    is_subadmin = models.BooleanField(default=False)
    sid = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\d{11}$', message="Phone number must be minimum 11 digits.")],
        help_text="Enter a valid phone number (e.g., +8801306609391).",
        null=True,
        blank=True,
    )
    institute = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    division = models.CharField(max_length=255, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username if self.user else "PublicUser"
    
    def save(self, *args, **kwargs):
        if not self.sid:  # If `sid` is not provided
            max_sid = PublicUser.objects.aggregate(models.Max('sid'))['sid__max']
            if max_sid:
                # Extract the numeric part of `sid` and increment it
                max_sid_number = int(max_sid.split('-')[1])  # Assuming `sid` is in the format "SAF-XXX"
                self.sid = f"SAF-{max_sid_number + 1:03d}"  # Format as a 3-digit string
            else:
                self.sid = "SAF-001"  # Default value if no existing `sid`
        super(PublicUser, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
       print('public user deleting')
       if self.tenant:
            try:
                schema_name = self.tenant.schema_name
                sql = f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    print('Schema Deleted')

                domain = self.tenant.domains.first()
                domain_obj =  Domain.objects.filter(domain=domain if domain else None).first()
                domain_obj.delete() if domain_obj else None
                print(f'Domain Deleted')
                tenant_obj = Tenant.objects.filter(id=self.tenant.id).first()
                tenant_obj.delete() if tenant_obj else None
                print(f'Tenant Deleted')
            except Exception as e:
                print(f'public user deleting error: {e}')
                
       super(PublicUser, self).delete(*args, **kwargs)