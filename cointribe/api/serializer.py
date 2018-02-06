from rest_framework import serializers
from inventory.models import Inventory,ModelApproval

class Loginserializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    redirect_url=serializers.URLField(max_length=200, min_length=None, allow_blank=True)

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"

class ModelApprovalSerializer(serializers.Serializer):
    action=serializers.CharField(required=True)
    admin_name=serializers.CharField(required=True)

