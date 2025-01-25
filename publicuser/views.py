from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django_tenants.utils import schema_context
from django.contrib.auth.models import User
from public.models import Tenant, Domain
from .models import PublicUser
from django.contrib.auth import authenticate, login, logout
from base.messages import sendmail
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
                    sendmail(name, message, subject, recipient_email, template_name, domain=False)
                    
                    public_user_obj, created_public = PublicUser.objects.get_or_create(
                        user=user_obj,
                        defaults={
                            'is_subadmin':False,
                            'phone':phone,
                            'institute':institute,
                            'description':colege_description,
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
        if requests:
            context.update({
                'requests': requests
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
            context.update({
                'requested_users': requested_users if requested_users else ''
            })
        except Exception as e:
            print(e)
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
        user_obj = User.objects.get(id=id)
        user_obj.delete()
        return redirect('requests')
        # if user_obj:
        #     public_user_obj = PublicUser.objects.filter(user=user_obj).first()
        #     print(public_user_obj)
        # return redirect('requests')


def requested_details(request, uid):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')
    context = {
        'active_url_name': 'requested_details'
    }
    current_schema = request.tenant.schema_name
    referal_url = request.GET.get('HTTP_REFERER', request.path_info)
    with schema_context(current_schema):
        public_user_obj = PublicUser.objects.get(uid=uid)
        if not public_user_obj:
            return HttpResponse(f'<h1> No User found </h1>')
        schema_objs = Tenant.objects.all()
        schemas = [s.schema_name for s in schema_objs]
        domain_objs = Domain.objects.all()
        domains = [d.domain for d in domain_objs]
        domain_lst = ['saf', 'localhost']
        for d in domains:
            dom = d.split('.')
            if len(dom) >= 2:
                domain_lst.append(dom[0])
        print(domain_lst)
        context.update({
            'page': f"{public_user_obj.user.first_name if public_user_obj.user.first_name else ''} {public_user_obj.user.last_name if public_user_obj.user.last_name else ''}",
            'user': public_user_obj ,
            'schemas': schemas,
            'domains': domain_lst,
        })

        if request.method == 'POST':
            institute = request.POST.get('institute', '')
            schema = request.POST.get('schema', '')
            subdomain = request.POST.get('sub-domain', '')
            fix_domain = request.POST.get('fix-domain', '')
            domain = request.POST.get('domain', '')
            if all([institute, subdomain, schema, fix_domain, domain]):
                try:
                    domian_name = f'{subdomain}.saf.localhost'
                    tenant_obj, tenant_created = Tenant.objects.get_or_create(
                        schema_name=schema,
                        defaults={
                            'name': institute,
                            'is_active': False,
                            'is_master': False,
                            'deadline': None,
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
                                'is_primary':True,
                                'domain':domian_name,
                            }
                        )
                        if created_domain:
                            name = f'{user.first_name} {user.last_name}'
                            message = f"We have successfully deployed your software. Thank you for choosing us!"
                            subject = 'Welcome to JS Technology'
                            recipient_email = [user.email,]
                            template_name = 'congratulate.html'
                            domain = domain_obj.domain
                            sendmail(name, message, subject, recipient_email, template_name, domain)
                            messages.info(request, f'Created Schema {schema} </br> Subdomain created {domain_obj.domain}')
                            return redirect('requests')

                except Exception as e:
                    print(e)
            return HttpResponseRedirect(referal_url)

    return render(request, 'public/dashboard/requested_details.html', context)

def users(request):
    context = {
        'page': 'SAF | Users',
        'user_link': 'users'
    }

    if not request.user.is_authenticated:
        messages.warning(request, 'Please Login First!')
        return redirect('login')
    current_schema = request.tenant.schema_name
    with schema_context(current_schema):
        users = User.objects.filter(is_active=True, is_superuser=False)
        context.update({
            'users': users
        })
    return render(request, 'public/dashboard/users.html', context)