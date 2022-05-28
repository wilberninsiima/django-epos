from django.db import models
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from datetime import datetime

# Create your models here.
class BaseModel(models.Model):
    created_by = CurrentUserField(editable=False,related_name="%(app_label)s_%(class)s_created_by",
        related_query_name="%(app_label)s_%(class)ss")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_by = CurrentUserField(on_update=True,related_name="%(app_label)s_%(class)s_updated_by",
        related_query_name="%(app_label)s_%(class)ss",verbose_name='last updated by')
    updated_at = models.DateTimeField(null=True,blank=True, editable=False,verbose_name='last updated on')

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     self.updated_at=datetime.now()
    #     super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract=True