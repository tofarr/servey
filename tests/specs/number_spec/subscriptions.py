from servey.action.action import get_action
from servey.security.access_control.allow_none import ALLOW_NONE
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.subscription.subscription import subscription
from tests.specs.number_spec.actions import integer_stats_consumer
from tests.specs.number_spec.models import IntegerStats


integer_stats_for_admins = subscription(
    event_type=IntegerStats,
    name="integer_stats_for_admins",
    access_control=ScopeAccessControl("root"),
)


integer_stats_queue = subscription(
    event_type=IntegerStats,
    name="integer_stats_queue",
    access_control=ALLOW_NONE,
    action_subscribers=(get_action(integer_stats_consumer),),
)
