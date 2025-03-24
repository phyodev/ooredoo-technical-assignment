from celery import shared_task
from django.utils import timezone
from .models import Redemption
import requests

@shared_task
def process_redemption(redemption_id):
    """
    Celery task to process a redemption asynchronously and call third-party API.
    """
    try:
        redemption = Redemption.objects.get(id=redemption_id)

        if redemption.status != 'pending':
            return f"Redemption {redemption_id} is already processed."

        # Simulate calling a third-party API
        api_url = "https://thirdparty.com/api/redeem"
        payload = {
            "customer_id": redemption.customer.id,
            "product_id": redemption.product.id,
        }
        response = requests.post(api_url, json=payload)

        # Handle API response
        if response.status_code == 200:
            redemption.status = 'success'
        else:
            redemption.status = 'failed'

        redemption.processed_at = timezone.now()
        redemption.save()

        return f"Redemption {redemption_id} processed with status: {redemption.status}"

    except Redemption.DoesNotExist:
        return f"Redemption {redemption_id} not found."
