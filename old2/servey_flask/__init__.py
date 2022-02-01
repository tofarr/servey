import os
from typing import Optional

from flask import Flask

from servey.servey_context import get_default_servey_context
from old2.servey_flask.flask_action_handler import FlaskActionHandler


def configure_flask(flask_instance: Optional[Flask] = None,
                    auth_cookie_name: str = os.environ.get('AUTH_COOKIE_NAME')
                    ) -> Flask:
    if flask_instance is None:
        flask_instance = Flask(__name__)
    servey_context = get_default_servey_context()
    for action in servey_context.actions_by_name.values():
        handler = FlaskActionHandler(action, auth_cookie_name)
        handler.register(flask_instance)
    return flask_instance


if __name__ == '__main__':
    import os
    app = configure_flask()
    app.run(
        host=os.environ.get('FLASK_HOST') or '',
        port=int(os.environ.get('FLASK_PORT') or '5000'),
        debug=True
    )
