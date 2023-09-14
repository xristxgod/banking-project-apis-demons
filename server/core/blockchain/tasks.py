from config import celery_app


@celery_app.task(acks_late=True)
def parsing_daemons_messages_task(message: dict):
    # TODO
    pass
