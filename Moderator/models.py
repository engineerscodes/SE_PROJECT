from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Mode(models.Model):
     #email=models.CharField(max_length=250,unique=True)
     email=models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
     mode_active=models.BooleanField(default=False)
     username=models.CharField(max_length=250,default='',unique=True)
     def __str__(self):
        return self.email.email +" is active :"+str(self.mode_active)