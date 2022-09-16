"""
Module for running a local python debugging server based on Uvicorn, along with a
local_schedule_mount for actions.
"""

import logging
import os

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)
DEBUG = int(os.environ.get("SERVER_DEBUG", "1")) == 1
HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "8000"))
CELERY_BROKER = os.environ.get('CELERY_BROKER')


def start_http_server():
    import uvicorn

    app = "servey.servey_starlette.starlette_app:app"
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level=LOGLEVEL.lower(),
        reload=DEBUG,
        reload_dirs=["."],
    )


def start_scheduler():
    if CELERY_BROKER:
        import servey.servey_celery.celery_app
    else:
        import servey.servey_thread.threaded_app


if __name__ == "__main__":
    start_http_server()
