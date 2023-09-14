import celery
from celery.schedules import crontab

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

app.conf.beat_schedule = {
    'parsing-crypto-rates': {
        'task': 'apps.exchange_rates.tasks.parsing_crypto_rates_task',
        'schedule': crontab(minute='*/5'),
    },
    'parsing-fiat-rates': {
        'task': 'apps.exchange_rates.tasks.parsing_fiat_rates_task',
        'schedule': crontab(day_of_week='*/1'),
    },
}
