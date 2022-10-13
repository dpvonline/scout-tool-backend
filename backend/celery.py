import os

from celery import Celery
from backend import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
use_celery = getattr(settings, 'USE_CELERY', False)

app = None
if use_celery:
    app = Celery("backend")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.control.purge()
    app.autodiscover_tasks()
