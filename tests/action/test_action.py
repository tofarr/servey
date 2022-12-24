from unittest import TestCase

from servey.action.action import action, get_action, Action
from servey.trigger.fixed_rate_trigger import FixedRateTrigger
from servey.trigger.web_trigger import WEB_GET
from servey.cache_control.ttl_cache_control import TtlCacheControl
from servey.action.example import Example
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.access_control.scope_access_control import ScopeAccessControl


class TestAction(TestCase):
    def test_decorator_no_args(self):
        # noinspection PyUnusedLocal
        @action
        def noop(value: int) -> str:
            """Noop"""

        action_ = get_action(noop)
        expected = Action(
            fn=noop,
            name="noop",
            description="Noop",
            access_control=ALLOW_ALL,
            triggers=tuple(),
            timeout=15,
            examples=None,
            cache_control=None,
        )
        self.assertEqual(expected, action_)

    def test_decorator_args(self):
        # noinspection PyUnusedLocal
        @action(
            access_control=ScopeAccessControl("execute"),
            triggers=(WEB_GET, FixedRateTrigger(3600)),
            timeout=30,
            examples=(Example(name="ten", params=dict(value=10), result="That's 10"),),
            cache_control=TtlCacheControl(900),
        )
        def noop(value: int) -> str:
            """Noop"""

        action_ = get_action(noop)
        expected = Action(
            fn=noop,
            name="noop",
            description="Noop",
            access_control=ScopeAccessControl("execute"),
            triggers=(WEB_GET, FixedRateTrigger(3600)),
            timeout=30,
            examples=(Example(name="ten", params=dict(value=10), result="That's 10"),),
            cache_control=TtlCacheControl(900),
        )
        self.assertEqual(expected, action_)
