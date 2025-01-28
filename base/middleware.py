from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_public_schema_name

class DebugTenantMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        hostname = self.hostname_from_request(request)
        print(f"Hostname: {hostname}")  # Debug hostname
        tenant_model = get_tenant_model()

        try:
            tenant = tenant_model.objects.get(domain__domain=hostname)
            print(f"Resolved Tenant: {tenant.schema_name}")  # Debug tenant
        except tenant_model.DoesNotExist:
            print("No matching tenant found. Falling back to public schema.")
            tenant = None

        super().process_request(request)
