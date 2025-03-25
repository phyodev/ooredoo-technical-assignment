from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import PointLedger, Redemption
from .serializers import PointLedgerSerializer, RedemptionSerializer
from .tasks import process_redemption
from .permissions import ReadOnlyPermission

class PointLedgerViewSet(viewsets.ModelViewSet):
    queryset = PointLedger.objects.all()
    serializer_class = PointLedgerSerializer
    permission_classes = [IsAuthenticated, ReadOnlyPermission]  # Requires authentication
    read_only_fields = ['points', 'expires_at']

    def get_queryset(self):
        return PointLedger.objects.filter(customer=self.request.user)  # Show only current user's points

class RedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Save redemption and trigger Celery task.
        """
        redemption = serializer.save(customer=self.request.user)
        process_redemption.delay(redemption.id, self.request.user.id)  # Run Celery in background

    ## Just using as Third Party Redeem API
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def redeem(self, request, pk=None):
        """
        Fulfill redemption locally when called by Celery.
        """
        try:
            redemption = Redemption.objects.get(id=pk)

            if redemption:
                return Response({"message": "Redemption fulfilled successfully!"}, status=status.HTTP_200_OK)

        except Redemption.DoesNotExist:
            return Response({"error": "Redemption not found"}, status=status.HTTP_404_NOT_FOUND)