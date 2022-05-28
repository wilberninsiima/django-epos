from django.apps import apps
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings

from django.contrib.auth.models import Permission
from django.db.models import Q
from django_currentuser.middleware import get_current_authenticated_user

# inject module atribute to the Django Permission model
# if not hasattr(Permission, 'module'):
#     module = models.CharField(max_length=100, blank=True, null=True)
#     module.contribute_to_class(Permission, 'module')

class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(
            self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

    def filter(self, **kwargs):
        if 'email' in kwargs:
            kwargs['email__iexact'] = kwargs['email']
            del kwargs['email']

        if 'username' in kwargs:  # Get by natural key not usef while registering, filter is
            kwargs['username__iexact'] = kwargs['username']
            del kwargs['username']
        return super(CustomUserManager, self).filter(**kwargs)

    def get(self, **kwargs):
        if 'email' in kwargs:
            kwargs['email__iexact'] = kwargs['email']
            del kwargs['email']

        if 'username' in kwargs:  # When we use .get() explicitly. Get by natural key used for logging in
            kwargs['username__iexact'] = kwargs['username']
            del kwargs['username']
        return super(CustomUserManager, self).get(**kwargs)


username_validator = RegexValidator(
    r'^[a-zA-Z0-9_\.]*$', 'Only alphanumeric characters, underscores, and periods are allowed in your username.')


class User(AbstractUser):
    username = models.CharField(max_length=255, blank=False, null=False, unique=True, validators=[])
    email = models.EmailField(max_length=255, blank=False, null=False, unique=True)
    first_name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    gender = models.CharField(max_length=255, blank=True, null=True,choices=settings.GENDER_CHOICES)
    profile_pic = models.ImageField(blank=True,null=True, upload_to='profile_pics')
    dob = models.DateField(max_length=45, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    # is_employee = models.BooleanField(default=False blank=True, null=True)
    nin = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    employee_number = models.CharField(max_length=255, blank=True, null=True)
    
    objects = CustomUserManager()

    def __str__(self):
        return "%s %s - (%s)"%(self.first_name,self.last_name,self.email)

    class Meta:
        permissions = (
            ("manage_user", "Can manage user"),
        )

    @property
    def full_name(self):
        if not self.first_name:return self.username
        return '%s %s'%(self.first_name,self.last_name)
    @property
    def name(self):
        if not self.first_name: return self.username
        return '%s %s'%(self.first_name,self.last_name)

    @property
    def thumbnail(self):
        if self.profile_pic:
            return "<div title='%s' class='member member--image'><img src='%s'/></div>"%(self.name,self.profile_pic.url)
        elif self.first_name:
            colors = ["red", "yellow", "blue"]
            val=ord(self.first_name[:1])
            return "<div title='%s' class='member member--%s'>%s</div>"%(self.name,colors[val%len(colors)],self.first_name[:1])
    
    
    @property
    def previous(self):
        current_user=get_current_authenticated_user()
        if current_user and current_user.has_perm('manage_user'):
            next_user=User.objects.filter(is_active=True,id__lt=self.id).order_by("-id").first()
            return next_user.id if next_user else None
    @property
    def next(self):
        current_user=get_current_authenticated_user()
        if current_user and current_user.has_perm('manage_user'):
            next_user=User.objects.filter(is_active=True,id__gt=self.id).order_by("id").first()
            return next_user.id if next_user else None

    @property
    def modules(self):
        if self.is_superuser:
            m= Permission.objects.all()
        else:
            m=Permission.objects.filter(Q(user=self) | Q(group__user=self)).distinct()
        m=m.filter(codename__endswith="module")#["administration_module","projects_module","hr_module","reports_module","inventory_module","suggestionbox_module","manage_archiving"])
        return m
        
