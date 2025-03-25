from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.conf import settings
from .models import Product
from points.models import PointLedger
from .serializers import ProductSerializer
from .permissions import ReadOnlyPermission

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # For GET requests
            return [AllowAny()]  # Allow unauthenticated access
        return [IsAuthenticated(), ReadOnlyPermission()]

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """
        Handle the purchase of a product, reward user with points in PointLedger.
        """
        try:
            # Get the product object
            product = self.get_object()

            ### Simulating the purchase process (this would normally be a payment gateway integration)
            purchase_success = True  # For now, we just simulate a successful purchase

            if purchase_success:
                points_earned = product.points_earned

                if request.user.tier == 'GOLD':
                    points_earned += settings.GOLD_TIER['EXTRA_POINTS']
                elif request.user.tier == 'Platinum':
                    points_earned += settings.PLATINUM_TIER['EXTRA_POINTS']

                # Add points to the user's PointLedger
                ledger_entry = PointLedger.objects.create(
                    customer=request.user,
                    points=points_earned,
                    expires_at=timezone.now() + timezone.timedelta(days=settings.POINTS_EXPIRY)  # Example expiration date
                )

                total_points = PointLedger.get_available_points(request.user)

                # Respond with a success message and the points added
                return Response({
                    "message": f"Product {product.name} purchased successfully! You've earned {points_earned} points.",
                    "total_points": total_points
                }, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Purchase failed."}, status=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)