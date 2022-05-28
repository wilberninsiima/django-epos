from django.shortcuts import render,get_object_or_404,HttpResponse,reverse
from django.views import View
from django.views.generic import ListView
from .forms import *

from .models import User
from core.models import *

from django.db.models import Case, When,Q,Count,F
from django.utils import timezone
from django.contrib.contenttypes.fields import ContentType
import datetime
from django.urls import reverse
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin

PER_PAGE=10

class GroupsView(PermissionRequiredMixin,ListView):
    permission_required = ('users.manage_user',)
    template_name="account/user-roles.html"
    paginate_by=40

    def get_template_names(self):
        if self.request.htmx:
            return 'account/partials/user-roles-section.html'
        return "account/user-roles.html"
    
    def get_queryset(self):
        return Group.objects.filter().prefetch_related("permissions")

    def get(self,request):
        page=request.GET.get("page",1)
        search=request.GET.get("search",None)
        groups =Group.objects.filter().order_by('name').prefetch_related("permissions")
        if search:
            groups=groups.filter(name__icontains=search)
        context={'list':groups}
        display=request.GET.get('display','section')
        if self.request.htmx:
            self.template_name= 'account/partials/user-roles-%s.html'%(display)
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=UserRoleForm()
            self.template_name="account/partials/user-role-form.html"
            return render(request, self.template_name,context)
        return render(request, self.template_name,context)
    
    def post(self, request, *args, **kwargs):
        form=UserRoleForm(request.POST)
        context={'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            self.template_name="account/partials/user-form.html"
            return render(request, self.template_name,context)


class GroupDetailView(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)

    def get(self, request, pk):
        display=request.GET.get('display','page')
        role = get_object_or_404(Group,pk=pk)
        context={
            'role':role,
            'form':UserRoleForm(instance=role)
        }
        self.template_name="account/partials/user-role-form.html"
        if display=='modal':
            self.template_name="account/partials/user-modal.html"
        return render(request, self.template_name,context)
    def post(self, request, pk):
        role = Group.objects.get(pk=pk)
        context={'role':role,}
        form =UserRoleForm(request.POST,request.FILES,instance=role)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            context['form']=form
            self.template_name="account/partials/user-role-form.html"
        return render(request, self.template_name,context)


class UsersView(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)
    template_name="account/users.html"

    def get(self,request):
        context={}
        status=self.request.GET.get('is_active', 1)
        perm=self.request.GET.get('permission', None)
        notme=self.request.GET.get('notme', None)
        filter=self.request.GET.get('filter', None)
        model=self.request.GET.get('model', None)
        model_id=self.request.GET.get('model_id', None)
        display=self.request.GET.get('display', 'all')
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=AddUserForm()
            self.template_name="account/partials/user-form.html"
            return render(request, self.template_name,context)
        role_names=Group.objects.only('name')
        users=User.objects.filter(is_active=status).prefetch_related('groups')

        if perm is not None:
            # Filter by the user specified permissions
            users=users.filter(Q(is_superuser=True) | Q(user_permissions__codename__in=[perm])|Q(groups__permissions__codename__in=[perm])).distinct()
        if notme is not None:
            # Remove the current logged in user from the list
            users=users.filter(is_active=status).exclude(id__in=[request.user.id])
        values_list=['id','employee_number','first_name','last_name','username','email','is_active','is_superuser','phone','designation','dob','gender','date_joined','last_login','nin','marital_status']
        if display=='summary':
            values_list=['id','first_name','last_name','email','is_active','is_superuser','phone','date_joined','last_login']
        context['users']=users
        context['list']=users.values(*values_list)
        if 'htmx' in request.GET:
            self.template_name="account/partials/users-list.html"
        return render(request, self.template_name,context)

    def post(self, request, format=None):
        form=AddUserForm(request.POST,request.FILES)
        context={'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            self.template_name="account/partials/user-form.html"
            return render(request, self.template_name,context)


class UserDetailView(LoginRequiredMixin,View):
    template_name="account/user.html"
    
    def get(self,request,pk):
        display=request.GET.get('display','page')
        user = get_object_or_404(User,pk=pk)
        context={
            'profile':user,
            'member':user
        }
        if request.GET.get('action',None)=='get-form':
            context['form']=AddUserForm(instance=user,initial={'pop-password':True})
            self.template_name="account/partials/user-form.html"
        if request.GET.get('action',None)=='get-password-reset-form':
            if user==request.user or request.user.has_perm('manage_user'):
                context['form']=CustomResetPasswordKeyForm()
                save_log("%s requested password reset form for %s"%(request.user,user))
            self.template_name="account/partials/password-reset-form.html"
        if display=='modal':
            payrollTermsList = [
                { "key": "allowances", "icon": "fa fa-arrow-up", "title": "Allowances" },
                { "key": "deductions", "icon": "fa fa-arrow-down", "title": "Deductions" },
                { "key": "taxes", "icon": "fa fa-arrow-down", "title": "Taxes" }
            ]
            context['payrollTermsList']=payrollTermsList
            # next_user=User.get_next_by_username(user)
            # print(next_user)
            self.template_name="account/partials/user-modal.html"
        return render(request, self.template_name,context)

    def post(self, request, pk):
        
        user = User.objects.get(pk=pk)
        context={
            'profile':user,
            'member':user
        }
        if request.GET.get('action',None)=='reset-password':
            form =CustomResetPasswordKeyForm(request.POST,user=user)
            if form.is_valid():
                form.save()
                save_log("%s changed password for %s"%(request.user,user))
                return HttpResponse("<div class='alert alert-success'>Password reset successfully</div>")
            else:
                context['form']=form
                self.template_name="account/partials/password-reset-form.html"
        else:
            form =AddUserForm(request.POST,request.FILES,instance=user,initial={'pop-password':True})
            if form.is_valid():
                form.save()
                # save_log("%s changed data for for %s"%(request.user,user))
                return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
            else:
                context['form']=form
                self.template_name="account/partials/user-form.html"
        return render(request, self.template_name,context)
        
    def delete(self, request, pk):
        user =User.objects.get(pk=pk)
        user.is_active=False
        user.save()
        return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
