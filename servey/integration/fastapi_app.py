"""
This module sets up a fastapi app using any default Action with a WebTrigger
to be run from a worker such as uvicorn.

To run directly with uvicorn, do `uvicorn -A servey.integration.celery_app worker --loglevel=INFO`
"""
import logging
import os

from fastapi import FastAPI

from servey.access_control.authorizer_factory_abc import create_authorizer
from servey.integration.fastapi_mount import FastapiMount

LOGGER = logging.getLogger(__name__)
TITLE = os.environ.get("FAST_API_TITLE") or "Servey"
VERSION = os.environ.get("FAST_API_VERSION") or "0.1.0"
SERVEY_FASTAPI_PATH = os.environ.get("SERVEY_FASTAPI_PATH") or "/actions/{action_name}"
api = FastAPI(title=TITLE, version=VERSION)
FastapiMount(api, create_authorizer(), SERVEY_FASTAPI_PATH).mount_all()
CELERY_BROKER = os.environ.get('CELERY_BROKER')

if CELERY_BROKER is None:
    # Single node / developer mode
    LOGGER.info('No CELERY_BROKER set - running background tasks locally.')
    from servey.integration.local_schedule_app import mount_all
    mount_all()
