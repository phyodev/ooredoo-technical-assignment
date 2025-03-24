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
        fields = '__all__'
        read_only_fields = ['status', 'created_at']  # Auto fields

    def create(self, validated_data):
        customer = validated_data['customer']
        product = validated_data['product']
        points_required = product.points_earned

        # Fetch available points, ordered by expiry date (oldest first)
        available_points = PointLedger.objects.filter(
            customer=customer, expires_at__gte=timezone.now(), is_used=False
        ).order_by('expires_at')

        total_available = sum(p.points for p in available_points)

        # Check if customer has enough points
        if total_available < points_required:
            raise serializers.ValidationError("Not enough points available for redemption.")

        # Deduct points starting from the oldest
        points_to_deduct = points_required
        for ledger_entry in available_points:
            if points_to_deduct <= 0:
                break
            if ledger_entry.points <= points_to_deduct:
                points_to_deduct -= ledger_entry.points
                # ledger_entry.is_used = True  # Mark as used
                ledger_entry.save()
            else:
                ledger_entry.points -= points_to_deduct
                ledger_entry.save()
                points_to_deduct = 0

        # Create redemption record
        redemption = Redemption.objects.create(**validated_data)

        # Call Celery task asynchronously
        from .tasks import process_redemption
        process_redemption.delay(redemption.id)

        return redemption
