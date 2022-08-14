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


def start_http_server():
    import uvicorn

    app = "servey.integration.fastapi_integration.fastapi_app:api"
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="debug",
        reload=True,
        reload_dirs=["."],
    )


if __name__ == "__main__":
    start_http_server()
