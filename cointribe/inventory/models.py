from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
# Create your models here.
STATUS=((1,"Approved"),(2,"Pending"),)
class Inventory(models.Model):
    productId=models.IntegerField()
    productName=models.CharField(max_length=200)
    vendor = models.CharField(max_length=50, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    batchNum =models.IntegerField()
    batchDate = models.DateField()
    quantity = models.IntegerField(default=0)
    status =models.IntegerField(choices=STATUS)
    updatedBy = models.ForeignKey('auth.User',null=True, blank=True)
    def __str__(self):
        return self.productName

class ModelApproval(models.Model):
    requestedBy=models.ForeignKey('auth.User',null=True, blank=True)
    action=models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    approve=models.BooleanField(default=False)
    approveBy=models.CharField(max_length=100,null=True, blank=True)
