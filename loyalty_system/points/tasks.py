from celery import shared_task
from django.utils import timezone
from .models import Redemption
from users.models import CustomUser
from points.models import PointLedger
import requests

@shared_task
def process_redemption(redemption_id, customer_id):
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
            customer = CustomUser.objects.get(id=customer_id)

            total_points = PointLedger.get_available_points(customer)
            if total_points >= redemption.product.points_earned:
                product_points = redemption.product.points_earned

                # Fetch all valid PointLedger entries for the customer (order by expiry date)
                point_ledgers = PointLedger.objects.filter(
                    customer=customer, expires_at__gt=timezone.now()
                ).order_by('expires_at')

                # substract product points from user total points
                substract_points = product_points
                for ledger in point_ledgers:
                    substract_points = substract_points - ledger.points
                    if substract_points < 0:
                        ledger.points = abs(substract_points)
                        ledger.save()
                        break
                    elif substract_points == 0:
                        ledger.delete()
                        break
                    elif substract_points > 0:
                        ledger.delete()
                        continue

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
