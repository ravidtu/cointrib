from django.contrib import admin
from .models import Inventory
# Register your models here.
class Inventory_Admin(admin.ModelAdmin):
    list_display = ('productId', 'productName', 'vendor','mrp')

admin.site.register(Inventory, Inventory_Admin)