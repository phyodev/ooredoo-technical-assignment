from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PointLedger, Redemption
from users.models import CustomUser
from .serializers import PointLedgerSerializer, RedemptionSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class PointLedgerViewSet(viewsets.ModelViewSet):
    queryset = PointLedger.objects.all()
    serializer_class = PointLedgerSerializer
    # permission_classes = [IsAuthenticated]  # Requires authentication

    def get_queryset(self):
        return PointLedger.objects.filter(customer=self.request.user)  # Show only current user's points

class RedemptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling product redemptions.
    """
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer
    # permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     customer = CustomUser.objects.get(user=self.request.user)  # Get logged-in customer
    #     serializer.save(customer=customer)

    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        """
        Process redemption locally instead of calling an external API.
        """
        try:
            # redemption = Redemption.objects.get(id=pk, customer__user=request.user)
            redemption = Redemption.objects.get(id=pk)

            if redemption.status != 'pending':
                return Response({"error": "Redemption already processed"}, status=status.HTTP_400_BAD_REQUEST)

            # Mark as success (simulating processing)
            redemption.status = 'success'
            redemption.processed_at = timezone.now()
            redemption.save()

            return Response({"message": "Redemption processed successfully!"}, status=status.HTTP_200_OK)

        except Redemption.DoesNotExist:
            return Response({"error": "Redemption not found"}, status=status.HTTP_404_NOT_FOUND)