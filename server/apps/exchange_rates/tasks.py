from config import celery_app


@celery_app.task(acks_late=True)
def parsing_crypto_rates_task():
    # TODO
    pass


@celery_app.task(acks_late=True)
def parsing_fiat_rates_task():
    # TODO
    pass
