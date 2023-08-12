from celery import Celery
# from celery.schedules import crontab

import settings

app = Celery('project')
app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks([

])

app.set_default()
app.conf.update(
    task_track_started=True,
    timezone='UTC',
)
