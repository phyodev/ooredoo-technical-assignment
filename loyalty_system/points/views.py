from rest_framework import viewsets
from .models import PointLedger
from .serializers import PointLedgerSerializer
from rest_framework.permissions import IsAuthenticated

class PointLedgerViewSet(viewsets.ModelViewSet):
    queryset = PointLedger.objects.all()
    serializer_class = PointLedgerSerializer
    # permission_classes = [IsAuthenticated]  # Requires authentication

    # def get_queryset(self):
    #     return PointLedger.objects.filter(customer=self.request.user)  # Show only current user's points