# loyalty_system/celery.py

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loyalty_system.settings')

app = Celery('loyalty_system')

app.conf.beat_schedule = {
    "remove-expired-points-daily": {
        "task": "points.tasks.remove_expired_points",
        "schedule": crontab(hour=0, minute=0),  # Runs every day at midnight
    },
}

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 👇 Force solo mode on Windows
if os.name == 'nt':  
    app.conf.worker_pool = 'solo'  

# Autodiscover tasks from Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
