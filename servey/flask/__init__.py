import os
from typing import Optional

from flask import Flask

from servey.servey_context import get_default_servey_context
from servey.flask.flask_action_handler import FlaskActionHandler


def configure_flask(app: Optional[Flask] = None,
                    auth_cookie_name: str = os.environ.get('AUTH_COOKIE_NAME')
                    ) -> Flask:
    if app is None:
        app = Flask(__name__)
    servey_context = get_default_servey_context()
    for action in servey_context.actions_by_name.values():
        handler = FlaskActionHandler(action, auth_cookie_name)
        handler.register(app)
    return app


if __name__ == '__main__':
    import os
    app = configure_flask()
    app.run(
        host=os.environ.get('FLASK_HOST') or '',
        port=int(os.environ.get('FLASK_PORT') or '8000'),
        debug=True
    )
