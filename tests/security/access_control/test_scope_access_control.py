from unittest import TestCase

from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import Authorization, PUBLIC


class TestScopeAccessControl(TestCase):
    def test_methods(self):
        access_control = ScopeAccessControl("view", "execute")
        view_only = Authorization(None, frozenset(["view"]), None, None)
        execute_only = Authorization(None, frozenset(["execute"]), None, None)
        view_and_execute = Authorization(
            None, frozenset(["view", "execute"]), None, None
        )
        self.assertFalse(access_control.is_executable(PUBLIC))
        self.assertFalse(access_control.is_viewable(PUBLIC))
        self.assertFalse(access_control.is_executable(view_only))
        self.assertTrue(access_control.is_viewable(view_only))
        self.assertTrue(access_control.is_executable(execute_only))
        self.assertFalse(access_control.is_viewable(execute_only))
        self.assertTrue(access_control.is_executable(view_and_execute))
        self.assertTrue(access_control.is_viewable(view_and_execute))

    def test_view_none(self):
        access_control = ScopeAccessControl(None, "execute")
        view_only = Authorization(None, frozenset(["view"]), None, None)
        execute_only = Authorization(None, frozenset(["execute"]), None, None)
        view_and_execute = Authorization(
            None, frozenset(["view", "execute"]), None, None
        )
        self.assertFalse(access_control.is_executable(PUBLIC))
        self.assertFalse(access_control.is_viewable(PUBLIC))
        self.assertFalse(access_control.is_executable(view_only))
        self.assertFalse(access_control.is_viewable(view_only))
        self.assertTrue(access_control.is_executable(execute_only))
        self.assertFalse(access_control.is_viewable(execute_only))
        self.assertTrue(access_control.is_executable(view_and_execute))
        self.assertFalse(access_control.is_viewable(view_and_execute))

    def test_execute_none(self):
        access_control = ScopeAccessControl("view", None)
        view_only = Authorization(None, frozenset(["view"]), None, None)
        execute_only = Authorization(None, frozenset(["execute"]), None, None)
        view_and_execute = Authorization(
            None, frozenset(["view", "execute"]), None, None
        )
        self.assertFalse(access_control.is_executable(PUBLIC))
        self.assertFalse(access_control.is_viewable(PUBLIC))
        self.assertFalse(access_control.is_executable(view_only))
        self.assertTrue(access_control.is_viewable(view_only))
        self.assertFalse(access_control.is_executable(execute_only))
        self.assertFalse(access_control.is_viewable(execute_only))
        self.assertFalse(access_control.is_executable(view_and_execute))
        self.assertTrue(access_control.is_viewable(view_and_execute))
