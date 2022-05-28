from django.contrib.auth.password_validation import validate_password
from django import forms
from django.contrib.auth.models import Group,Permission
from allauth.account.forms import LoginForm,SignupForm,ResetPasswordForm,SetPasswordForm,ResetPasswordKeyForm
from django.conf import settings
from .models import *
from django.contrib.admin import widgets

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div


excludedContentTypePermissions=["payrollaprover","site",'salesitem',"logentry","log","emailaddress","emailconfirmation","config","notification","socialaccount","socialapp","socialtoken","permission","contenttype","session"]

class UserRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)
        perms=Permission.objects.filter().exclude(content_type__model__in=excludedContentTypePermissions)
        if 'permissions' in self.fields:self.fields['permissions'].queryset=perms
        # Arrange columns as in crispy
        self.helper = FormHelper()
    class Meta:
        model=Group
        fields='__all__'
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            # 'permissions':forms.SelectMultiple(attrs={'class':'form-control'}),
            'permissions':forms.CheckboxSelectMultiple(),
        }


class AddUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First Name',required=True)
    last_name = forms.CharField(max_length=30, label='Last Name',required=True)
    col1_fields=['first_name','last_name','employment_type','gender','email','username','password','is_active']
    col2_fields=['employee_number','phone','nin','profile_pic','date_joined','is_superuser']
    row2_fields=['groups']
    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields and 'initial' in kwargs and kwargs['initial'].get("pop-password",None):
            del self.fields['password']
        if 'groups' in self.fields:
            self.fields['groups'].label="Role(s)"
        
        perms=Permission.objects.filter().exclude(content_type__model__in=excludedContentTypePermissions)
        if 'user_permissions' in self.fields:self.fields['user_permissions'].queryset=perms
        
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        # if 'country' in self.fields:self.fields['country'].widget = forms.Select(attrs={'class': 'form-control form-control-lg'},choices=settings.COUNTRIES_CHOICES)
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control'})
        if 'password' in self.fields:
            self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
            self.fields['password'].required=False
            self.fields['password'].validators=[validate_password]
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

        

        # Arrange columns as in crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(*self.col1_fields, css_class='col-sm-6'),
                Div(*self.col2_fields, css_class='col-sm-6'), css_class='row'
            ),
            Div(
                Div(Div(*self.row2_fields), css_class='col-md-12'), css_class='row'
            )
        )

    class Meta:
        model=User
        fields='__all__'
        fields=['first_name','last_name','email','username','password','is_active','employee_number','phone','gender','nin','profile_pic','date_joined','is_superuser','groups','user_permissions']
        widgets={
            # 'date_joined':forms.DateInput(attrs={'type': 'datetime-local'}),
            'dob':forms.DateInput(attrs={'type': 'date'}),
            'gender':forms.Select(attrs={'class':'form-control'}),
            'groups':forms.SelectMultiple(attrs={'class':'form-control'}),
            'user_permissions':forms.SelectMultiple(attrs={'class':'form-control'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'password' in self.cleaned_data:
            print("Password found")
            password = self.cleaned_data.pop('password')
            if password and password!="":
                instance.set_password(password)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        if 'login' in self.fields:self.fields['login'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg','autofocus':'true'})
        if 'password' in self.fields:self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control form-control-lg'})
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})

    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.country = self.cleaned_data['country']
        user.save()
        return user


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        if 'login' in self.fields:self.fields['login'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg','autofocus':'true'})
        if 'password' in self.fields:self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        # if 'country' in self.fields:self.fields['country'].widget = forms.Select(attrs={'class': 'form-control form-control-lg'},choices=settings.COUNTRIES_CHOICES)
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control form-control-lg'})
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})

    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.country = self.cleaned_data['country']
        user.save()
        return user


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control form-control-lg'})


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})

class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordKeyForm, self).__init__(*args, **kwargs)
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg-'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg-'})