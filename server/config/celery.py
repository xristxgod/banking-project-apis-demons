import celery

import settings

app = celery.Celery('merchant')
app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks([
    'core.blockchain.tasks',
    'apps.exchange_rates.tasks',
])
app.set_default()
app.conf.update(
    task_track_started=True,
    timezone='UTC',
)

app.conf.beat_schedule = {}
