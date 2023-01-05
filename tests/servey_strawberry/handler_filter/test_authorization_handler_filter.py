import inspect
from collections import namedtuple
from unittest import TestCase

from starlette.requests import Request
from strawberry.types import Info

from servey.action.action import action, get_action
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import Authorization, ROOT, AuthorizationError
from servey.servey_strawberry.handler_filter.authorization_handler_filter import (
    AuthorizationHandlerFilter,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


class TestAuthorizationHandlerFilter(TestCase):
    def filtered_action(self):
        # noinspection PyUnusedLocal
        @action(access_control=ScopeAccessControl("root"))
        def dummy(title: str, auth: Authorization) -> str:
            """Dummy"""

        action_ = get_action(dummy)
        filter_ = AuthorizationHandlerFilter()
        schema_factory = SchemaFactory()
        filtered_action, continue_filtering = filter_.filter(action_, schema_factory)
        self.assertTrue(continue_filtering)

        sig = inspect.signature(filtered_action.fn)
        params = list(sig.parameters.values())
        expected_params = [
            inspect.Parameter(
                "title", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str
            ),
            inspect.Parameter("info", inspect.Parameter.KEYWORD_ONLY, annotation=Info),
        ]
        self.assertEqual(expected_params, params)
        return filtered_action, filter_

    def test_filter(self):
        filtered_action, filter_ = self.filtered_action()
        token = filter_.authorizer.encode(ROOT)
        request = Request(
            dict(
                method="GET",
                type="http",
                headers=[
                    [
                        "authorization".encode("latin-1"),
                        f"Bearer {token}".encode("latin-1"),
                    ]
                ],
            )
        )
        context = dict(request=request)
        raw_info = namedtuple("RawInfo", ["context"])(context=context)
        # noinspection PyTypeChecker
        info = Info(raw_info, None)
        filtered_action.fn(title="foobar", info=info)
        filtered_action.fn(title="foobar", info=info)

    def test_filter_no_auth(self):
        filtered_action, filter_ = self.filtered_action()
        request = Request(dict(method="GET", type="http", headers=[]))
        context = dict(request=request)
        raw_info = namedtuple("RawInfo", ["context"])(context=context)
        # noinspection PyTypeChecker
        info = Info(raw_info, None)
        with self.assertRaises(AuthorizationError):
            filtered_action.fn(title="foobar", info=info)
