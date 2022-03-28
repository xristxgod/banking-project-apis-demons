from celery import Celery
from config import INTERNAL_RABBIT_URL


celery_app = Celery(
    "worker",
    backend="redis://:password123@bsc_redis:6379/0",
    broker=INTERNAL_RABBIT_URL
)
celery_app.conf.task_routes = {
    "worker.celery_worker.send_transaction": "test-queue"
}

celery_app.conf.update(task_track_started=True)
