from mangum import Mangum

from servey.action_context import get_default_action_context
from servey.integration.starlette_integ.starlette_app import app


_MANGUM_APP = Mangum(app)
_ACTION_CONTEXT = get_default_action_context()

for _action in get_default_action_context().get_actions():
    globals()[_action.action_meta.name] = LambdaActionHandler(
        _action,
        _MANGUM_APP,
    )
