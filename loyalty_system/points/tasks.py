from celery import shared_task
from .models import Redemption
import requests

@shared_task
def process_redemption(redemption_id):
    """
    Celery task to process redemption by calling the local redeem API.
    """
    try:
        redemption = Redemption.objects.get(id=redemption_id)

        if redemption.status != "pending":
            return f"Redemption {redemption_id} already processed. It was {redemption.status}"


        url = f"http://127.0.0.1:8000/api/redemptions/{redemption_id}/redeem/"
        response = requests.post(url, verify=False) # Disable SSL verification for just local development

        if response.status_code == 200:
            redemption.status = "success"
            redemption.save()
            return f"Redemption {redemption_id} successfully redeemed!"
        else:
            redemption.status = "failed"
            redemption.save()
            return f"Redemption {redemption_id} processed, but redeem action failed."

    except Redemption.DoesNotExist:
        return f"Redemption {redemption_id} not found."
    except Exception as e:
        return f"Error processing redemption {redemption_id}: {str(e)}"
