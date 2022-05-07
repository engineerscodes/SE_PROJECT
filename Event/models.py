from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Event(models.Model):

    eventname = models.CharField(max_length=50,unique=True)
    lastDate=models.DateField(default='2001-04-12')
    maxMarks=models.IntegerField(default=100,validators=[ MaxValueValidator(100),MinValueValidator(1)])
    def __str__(self):
        return self.eventname