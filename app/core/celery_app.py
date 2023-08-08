import os

from celery import Celery

CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://queue/1")

celery_app = Celery("worker", broker="redis://queue/0", backend=CELERY_RESULT_BACKEND)
