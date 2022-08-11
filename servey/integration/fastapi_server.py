from logging import getLogger
import os

from servey.action_finder import find_actions
from servey.integration.fastapi_mount import FastapiMount
from servey.servey_error import ServeyError

DEBUG = int(os.environ.get("SERVER_DEBUG", "1")) == 1
HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "8000"))
LOGGER = getLogger(__name__)


def create_fastapi_app():
    try:
        from fastapi import FastAPI
        api = FastAPI(
            title=os.environ.get("FAST_API_TITLE") or "Servey",
            version=os.environ.get("FAST_API_VERSION") or "0.1.0",
        )
        return api
    except ModuleNotFoundError:
        raise ServeyError(
            "FastAPI not found: Run `pip install fastapi`"
        )


def mount_servey_actions(api):
    servey_action_path = os.environ.get('SERVEY_ACTION_PATH') or 'debuggery.foobar'
    if servey_action_path is None:
        raise ServeyError('Please specify SERVEY_ACTION_PATH in your environment.')
    mount = FastapiMount(api, os.environ.get("SERVEY_FASTAPI_PATH") or "/actions/{action_name}")
    found_actions = find_actions([servey_action_path])
    actions = (a.action for a in found_actions)
    mount.mount_actions(actions)
    LOGGER.info("Action routes mounted...")


app = create_fastapi_app()
if app:
    mount_servey_actions(app)


if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError:
        raise ValueError("Additional Packages Required. Run `pip install uvicorn`")

    app = "servey.integration.fastapi_server:app"
    print(f"Running persisty on http://{HOST}:{PORT}/")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="debug",
        reload=True,
        reload_dirs=["."],
    )
