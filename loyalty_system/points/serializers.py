from rest_framework import serializers
from .models import PointLedger, Redemption
from .models import Redemption
from users.models import CustomUser
from products.models import Product
from points.models import PointLedger
from django.utils import timezone

class PointLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointLedger
        fields = '__all__'  # Includes all fields
        read_only_fields = ['expires_at', 'created_at']  # Auto fields

class RedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redemption
        fields = ['id', 'customer', 'product', 'status', 'created_at']
        read_only_fields = ['customer']

    def validate(self, data):
        """
        Check if the customer has enough points before redeeming.
        """
        product = data['product']
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is missing.")

        # Get total available points
        total_points = PointLedger.get_available_points(request.user)

        if total_points < product.points_earned:
            raise serializers.ValidationError("Not enough points to redeem this product.")

        return data
