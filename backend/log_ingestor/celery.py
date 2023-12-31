# celery.py
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_ingestor.settings')

# create a Celery instance and configure it with the Django settings.
app = Celery('log_ingestor')

# specify the namespace for tasks to avoid naming conflicts with other Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
