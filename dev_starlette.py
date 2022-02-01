import os
import uvicorn

from servey.servey_starlette.servey_starlette_app import new_default_starlette

UVICORN_HOST = os.environ.get('UVICORN_HOST') or '127.0.0.1'
UVICORN_PORT = int(os.environ.get('UVICORN_PORT') or '8000')
LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'info'

app = new_default_starlette()

if __name__ == '__main__':
    uvicorn.run(f"{__name__}:app", host=UVICORN_HOST, port=UVICORN_PORT, log_level=LOG_LEVEL)
