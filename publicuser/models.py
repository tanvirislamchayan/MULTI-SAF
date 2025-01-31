import os
from django.db import models, connection
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django_tenants.utils import schema_exists
from django.conf import settings
from base.models import BaseModel
from public.models import Tenant, Domain

class PublicUser(BaseModel):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name='public_user')
    is_subadmin = models.BooleanField(default=False)
    sid = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='cover_pics/', null=True, blank=True)
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

    def delete_old_image(self, old_image_path):
        """Delete the old image file from storage if it exists."""
        if old_image_path and os.path.isfile(os.path.join(settings.MEDIA_ROOT, old_image_path)):
            os.remove(os.path.join(settings.MEDIA_ROOT, old_image_path))

    def save(self, *args, **kwargs):
        # Get the existing instance from the database if it exists
        if self.pk:
            existing_user = PublicUser.objects.filter(pk=self.pk).first()
            
            # If profile image is updated, delete the old one
            if existing_user and existing_user.profile_image and self.profile_image != existing_user.profile_image:
                self.delete_old_image(existing_user.profile_image.path)
            
            # If cover image is updated, delete the old one
            if existing_user and existing_user.cover_image and self.cover_image != existing_user.cover_image:
                self.delete_old_image(existing_user.cover_image.path)

        # Generate SID if not provided
        if not self.sid:
            max_sid = PublicUser.objects.aggregate(models.Max('sid'))['sid__max']
            if max_sid:
                max_sid_number = int(max_sid.split('-')[1])  # Assuming `sid` format is "SAF-XXX"
                self.sid = f"SAF-{max_sid_number + 1:03d}"  # Format as 3-digit string
            else:
                self.sid = "SAF-001"  # Default SID

        super(PublicUser, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete associated images and tenant schema when deleting user."""
        print('Public user deleting')
        
        # Delete associated images
        if self.profile_image:
            self.delete_old_image(self.profile_image.path)
        if self.cover_image:
            self.delete_old_image(self.cover_image.path)

        # Delete tenant schema if it exists
        if self.tenant:
            try:
                schema_name = self.tenant.schema_name
                sql = f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    print('Schema Deleted')

                domain = self.tenant.domains.first()
                domain_obj = Domain.objects.filter(domain=domain if domain else None).first()
                domain_obj.delete() if domain_obj else None
                print('Domain Deleted')
                
                tenant_obj = Tenant.objects.filter(id=self.tenant.id).first()
                tenant_obj.delete() if tenant_obj else None
                print('Tenant Deleted')

            except Exception as e:
                print(f'Public user deleting error: {e}')
                
        super(PublicUser, self).delete(*args, **kwargs)
