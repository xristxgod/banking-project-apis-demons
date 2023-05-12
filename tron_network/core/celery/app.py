import celery

import settings

main_queue = 'main-queue'

app = celery.Celery(
    'worker',
    backend=settings.REDIS_URL,
    broker=settings.RABBITMQ_URL,

    tasks={
        'core.celery.tasks.send_to_central_wallet': main_queue,
        'core.celery.tasks.approve_to_central_wallet': main_queue,
        'core.celery.tasks.freeze_central_balance': main_queue,
        'core.celery.tasks.unfreeze_central_balance': main_queue,
    }
)

app.conf.update(task_track_started=True)
