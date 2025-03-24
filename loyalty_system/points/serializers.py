from rest_framework import serializers
from .models import PointLedger

class PointLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointLedger
        fields = '__all__'  # Includes all fields
        read_only_fields = ['expires_at', 'created_at']  # Auto fields
