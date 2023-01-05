import os


def has_celery_broker():
    return bool(os.environ.get("CELERY_BROKER"))
