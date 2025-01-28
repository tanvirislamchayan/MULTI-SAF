from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django_tenants.utils import schema_context
from django.contrib.auth.models import User
from public.models import Tenant, Domain
from .models import PublicUser
from django.contrib.auth import authenticate, login, logout
from base.messages import sendmail
from django.db import transaction
from django.db.models import Q
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
from django.core.paginator import Paginator
# Create your views here.

def index(request):
    return redirect('login')

def user_register(request):
    current_schema = request.tenant.schema_name
    referal_url = request.META.get('HTTP_REFERER', request.path_info)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        institute = request.POST.get('institute', '')
        colege_description = request.POST.get('colege_description', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        con_pass = request.POST.get('con_pass', '')
        district = request.POST.get('district', '')
        division = request.POST.get('division', '')
        if password != con_pass:
            messages.warning(request, "password doesn't match")
            return HttpResponseRedirect(referal_url)

        with schema_context(current_schema):
            try:
                user_obj, created = User.objects.get_or_create(
                    username=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_active':False,
                        'is_staff':False,
                        'is_superuser':False,
                    }
                )

                if created:
                    user_obj.set_password(password)
                    user_obj.save()
                    # send mail
                    name = f'{user_obj.first_name} {user_obj.last_name}'
                    message = f"We have successfully received your request! Your software will be ready within 1 to 2 hours. Our team will contact you shortly through email once it's completed. Thank you for choosing us!"
                    subject = 'Welcome to JS Technology'
                    recipient_email = [user_obj.email,]
                    template_name = 'congratulate.html'
                    sendmail(name, message, subject, recipient_email, template_name, domain=False, context=None)
                    
                    public_user_obj, created_public = PublicUser.objects.get_or_create(
                        user=user_obj,
                        defaults={
                            'is_subadmin':False,
                            'phone':phone,
                            'institute':institute,
                            'description':colege_description,
                            'district':district,
                            'division':division,
                        }
                    )
                    if created_public:

                        messages.info(
                            request,
                            f"<h3 class='p-0 m-0'>🎉 Congratulations!</h3>"
                            f"<hr class='my-2' />"
                            f"We have successfully received your request! Your software will be ready within 1 to 2 hours. "
                            f"Our team will contact you shortly through email once it's completed. Thank you for choosing us!"
                        )
                        return redirect('login')
                else:
                    messages.warning(request, 'User already exist.')
                    return HttpResponseRedirect(referal_url)
            except Exception as e:
                print(e)
    return render(request, 'public/register_form.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    referal_url = request.META.get('HTTP_REFERER', request.path_info)
    current_schema = request.tenant.schema_name
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if not all([username, password]):
            messages.error(request, 'Username and Password both are required')
            return HttpResponseRedirect(referal_url)
        with schema_context(current_schema):
            try:
                user = authenticate(username=username, password=password)
                if user:
                    print(user)
                    login(request, user)
                    messages.success(request, f'Welcome back {user.first_name} {user.last_name}')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid Username or Password')
                    return HttpResponseRedirect(referal_url)
            except Exception as e:
                print(e)
    return render(request, 'public/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


def dashboard(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')
    current_schema = request.tenant.schema_name
    context = {
        'page': 'SAF | Dashboard',
    }
    with schema_context(current_schema):
        requests = User.objects.filter(is_active=False)
        total_requests = User.objects.filter(is_active=False).count()
        total_users = User.objects.filter(is_active=True, is_superuser=False, is_staff=False).count()
        total_active_users = PublicUser.objects.filter(tenant__is_active=True, user__is_active=True, user__is_superuser=False, user__is_staff=False).count()
        if requests:
            context.update({
                'requests': requests,
                'total_requests': total_requests,
                'total_users': total_users,
                'total_active_users': total_active_users,
            })
    return render(request, 'public/dashboard/dashboard.html', context)


def user_requests(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')

    current_schema = request.tenant.schema_name
    referal_url = request.META.get('HTTP_REFERER', request.path_info)
    context = {
        'page': 'SAF | Requests',
        'active_url_name': 'requests'
    }

    with schema_context(current_schema):
        try:
            requested_users = User.objects.filter(is_active=False)
            
            # Handle search functionality
            if 'search' in request.GET:
                search_term = request.GET.get('search', '').strip()
                if search_term:
                    requested_users = requested_users.filter(
                        Q(username__icontains=search_term) |
                        Q(email__icontains=search_term) |
                        Q(first_name__icontains=search_term) |
                        Q(last_name__icontains=search_term) |
                        Q(public_user__phone__icontains=search_term) |
                        Q(public_user__institute__icontains=search_term) |
                        Q(public_user__description__icontains=search_term) |
                        Q(public_user__district__icontains=search_term) |
                        Q(public_user__division__icontains=search_term) |
                        Q(public_user__sid__icontains=search_term) |
                        Q(public_user__tenant__schema_name__icontains=search_term) |
                        Q(public_user__tenant__name__icontains=search_term) |
                        Q(public_user__tenant__domains__domain__icontains=search_term) 
                    )
            
            # Add pagination logic
            paginator = Paginator(requested_users, 20)  # 20 users per page
            page_number = request.GET.get('page')
            paginated_requested_users = paginator.get_page(page_number)

            context.update({
                'requested_users': paginated_requested_users,
                'page_obj': paginated_requested_users,  # Add for pagination controls
            })

        except Exception as e:
            print(e)
    
    # Handle redirect logic
    if 'uid' in request.GET:
        uid = request.GET.get('uid')
        if uid:
            return redirect('requested_details', uid=uid)
    if 'delete' in request.GET:
        id = request.GET.get('delete', '')
        if id:
            return redirect('delete_user', id=id)
        
    return render(request, 'public/dashboard/requests.html', context)

def delete_user(request, id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')
    current_schema = request.tenant.schema_name
    with schema_context(current_schema):
        try:

            public_user = None
            tenant = None
            domain_obj = None
            user_obj = User.objects.get(id=id)
            print(f'user: {user_obj}')

            if user_obj:
                user_name = f"{user_obj.first_name} {user_obj.last_name if user_obj.last_name else ''}"
                public_user = PublicUser.objects.filter(user=user_obj).first()
                public_user.delete() if public_user else None
                user_obj.delete()
                messages.info(request, f'User deleted {user_name}')
        except Exception as e:
            print(e)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', request.path_info))


def requested_details(request, uid):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')

    context = {
        'active_url_name': 'requested_details',
        'bg_link': 'requested_details'
    }
    current_schema = request.tenant.schema_name
    referal_url = request.GET.get('HTTP_REFERER', request.path_info)

    with schema_context(current_schema):  # Ensure schema context is set for this operation
        try:
            public_user_obj = PublicUser.objects.get(uid=uid)
        except PublicUser.DoesNotExist:
            return HttpResponse('<h1>No User found</h1>')

        schema_objs = Tenant.objects.all()
        schemas = [s.schema_name for s in schema_objs]
        domain_objs = Domain.objects.all()
        domains = [d.domain for d in domain_objs]
        domain_lst = ['saf', 'localhost']
        for d in domains:
            dom = d.split('.')
            if len(dom) >= 2:
                domain_lst.append(dom[0])
        context.update({
            'page': f"{public_user_obj.user.first_name if public_user_obj.user.first_name else ''} {public_user_obj.user.last_name if public_user_obj.user.last_name else ''}",
            'user': public_user_obj,
            'schemas': schemas,
            'domains': domain_lst,
        })

        if request.method == 'POST':
            institute = request.POST.get('institute', '')
            schema = request.POST.get('schema', '')
            subdomain = request.POST.get('sub-domain', '')
            fix_domain = request.POST.get('fix-domain', '')
            domain = request.POST.get('domain', '')
            status = request.POST.get('status', '')
            deadline = request.POST.get('deadline', '')
            

            if all([institute, subdomain, schema, fix_domain, domain, status, deadline]):
                try:
                    with transaction.atomic():  # Start a transaction block
                        # Ensure the domain name format is correct
                        domian_name = f'{subdomain}.saf.localhost'

                        # Ensure we're in the correct schema context when creating or fetching tenant
                        with schema_context(current_schema):  # Set schema context here as well
                            tenant_obj, tenant_created = Tenant.objects.get_or_create(
                                schema_name=schema,
                                defaults={
                                    'name': institute,
                                    'is_active': True if status == 'true' else False,
                                    'is_master': False,
                                    'deadline': deadline if deadline else None,
                                    'favicon': None,
                                }
                            )
                            if tenant_created:
                                user = public_user_obj.user
                                user.is_active = True
                                user.save()
                                public_user_obj.tenant = tenant_obj
                                public_user_obj.is_subadmin = True
                                public_user_obj.save()

                            domain_obj, created_domain = Domain.objects.get_or_create(
                                tenant=tenant_obj,
                                defaults={
                                    'is_primary': True,
                                    'domain': domian_name,
                                }
                            )

                            if created_domain:
                                name = f'{user.first_name} {user.last_name}'
                                message = "We have successfully deployed your software. Thank you for choosing us!"
                                subject = 'Welcome to JS Technology'
                                
                                # Validate email address before sending
                                try:
                                    validate_email(user.email)
                                    recipient_email = [user.email]
                                except ValidationError:
                                    raise ValueError(f"Invalid email address: {user.email}")
                                
                                template_name = 'approved.html'
                                sendmail(name, message, subject, recipient_email, template_name, domain_obj.domain, context=None)
                                messages.info(request, f'Created Schema {schema}. Subdomain created {domain_obj.domain}')
                                return redirect('requests')

                except Exception as e:
                    # If any error occurs, delete everything created so far
                    if tenant_obj:
                        tenant_obj.delete()
                    if domain_obj:
                        domain_obj.delete()
                    if public_user_obj:
                        public_user_obj.tenant = None
                        public_user_obj.is_subadmin = False
                        public_user_obj.save()

                    messages.error(request, f"Error: {str(e)}")
                    transaction.rollback()  # Rollback the transaction to ensure nothing is committed
                    messages.error(request, "Something went wrong, and all changes have been rolled back.")
                return HttpResponseRedirect(referal_url)
            else:
                messages.warning(request, 'Please fill all fields.')
                return HttpResponseRedirect(referal_url)

    return render(request, 'public/dashboard/requested_details.html', context)


def users(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')

    context = {
        'page': 'SAF | Users',
        'user_link': 'users'
    }

    current_schema = request.tenant.schema_name
    with schema_context(current_schema):
        users = User.objects.filter(is_active=True, is_superuser=False)
        
        # Handle search functionality
        if 'search' in request.GET:
            search_term = request.GET.get('search', '').strip()
            if search_term:
                users = users.filter(
                    Q(username__icontains=search_term) |
                    Q(email__icontains=search_term) |
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(public_user__phone__icontains=search_term) |
                    Q(public_user__institute__icontains=search_term) |
                    Q(public_user__description__icontains=search_term) |
                    Q(public_user__district__icontains=search_term) |
                    Q(public_user__division__icontains=search_term) |
                    Q(public_user__sid__icontains=search_term) |
                    Q(public_user__tenant__schema_name__icontains=search_term) |
                    Q(public_user__tenant__name__icontains=search_term) |
                    Q(public_user__tenant__domains__domain__icontains=search_term) 
                )

        # Add pagination logic
        paginator = Paginator(users, 20)  # 20 users per page
        page_number = request.GET.get('page')
        paginated_users = paginator.get_page(page_number)

        context.update({
            'users': paginated_users,
            'page_obj': paginated_users,  # Add for pagination controls
        })

    return render(request, 'public/dashboard/users.html', context)


def user_details(request, uid):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')

    public_user = None
    context = {
        'page': 'SAF | USER',
        'user_link': 'user_details',
        'bg_link': 'user_details'
    }
    current_schema = request.tenant.schema_name
    with schema_context(current_schema):
        public_user = PublicUser.objects.filter(uid=uid).first()
        if public_user:
            context.update({
                'page': f'SAF | {public_user.user.first_name} {public_user.user.last_name}',
                'user': public_user
            })
        else:
            return redirect('users')

    return render(request, 'public/dashboard/user_details.html', context)


def tenant_status(request, uid):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')

    referal_url = request.META.get('HTTP_REFERER', request.path_info)
    current_schema = request.tenant.schema_name
    try:
        if not uid:
            messages.error(request,'No UID found!')
        with schema_context(current_schema):
            public_user = PublicUser.objects.filter(uid=uid).first()
            if public_user :
                tenant_obj = public_user.tenant
                if tenant_obj and not tenant_obj.deadline:
                    messages.warning(request, 'Please add "Deadline" first!')
                    return redirect('user_update', public_user.uid)
                if tenant_obj and tenant_obj.is_active:
                    tenant_obj.is_active = False
                    tenant_obj.save()
                    messages.warning(request, 'Deactivated')
                elif tenant_obj and not tenant_obj.is_active:
                    tenant_obj.is_active = True
                    tenant_obj.save()
                    messages.success(request, 'Activated')
                else:
                    messages(request, 'No schema available.')
                
    except Exception as e:
        print(e)
    return HttpResponseRedirect(referal_url)


def user_update(request, uid):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')
    current_schema = request.tenant.schema_name
    referal_url = request.META.get('HTTP_REFERER', request.path_info)
    public_user = None
    context = {
        'page': 'SAF | USER',
        'user_link': 'user_update',
        'bg_link': 'user_update'
    }
    if not uid:
        messages.error(request, 'No UID Found')
        return HttpResponseRedirect(referal_url)
    with schema_context(current_schema):
        schema_objs = Tenant.objects.all()
        schemas = [s.schema_name for s in schema_objs]
        domain_objs = Domain.objects.all()
        domains = [d.domain for d in domain_objs]
        domain_lst = ['saf', 'localhost']
        for d in domains:
            dom = d.split('.')
            if len(dom) >= 2:
                domain_lst.append(dom[0])
        context.update({
            'schemas': schemas,
            'domains': domain_lst,
        })

        public_user = PublicUser.objects.filter(uid=uid).first()
        if public_user:
            context.update({
                'page': f'SAF | {public_user.user.first_name} {public_user.user.last_name}',
                'user': public_user
            })

        if request.method == 'POST' and public_user:
            try:

                schema = request.POST.get('schema', '')
                status = request.POST.get('status', '')
                deadline = request.POST.get('deadline', '')
                subdomain = request.POST.get('sub-domain', '')
                print(status)

                tenant_obj = public_user.tenant
                if tenant_obj:
                    tenant_obj.is_active = True if status == 'true' else False
                    tenant_obj.deadline = deadline
                    tenant_obj.save()
                    domain = f'{subdomain}.saf.localhost'
                    domain_obj = tenant_obj.domains.first()
                    domain_obj.domain = domain
                    domain_obj.save()
                    if tenant_obj.schema_name != schema:
                        sql = f"ALTER SCHEMA {tenant_obj.schema_name} RENAME TO {schema}" #Change schema name
                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                        tenant_obj.schema_name = schema
                        tenant_obj.save()
                    messages.success(request, 'Updated user successfully')
                    return redirect('user_details', public_user.uid)
            except Exception as e:
                print(e)
                messages.error(request, 'Something went wrong')
                return HttpResponseRedirect(referal_url)

    return render(request, 'public/dashboard/edit_user.html', context)


def profile(request):
    return render(request, 'public/dashboard/profile.html')