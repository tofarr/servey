from datetime import datetime
from unittest import TestCase

from dateutil.relativedelta import relativedelta

from servey.security.authorization import (
    Authorization,
    AuthorizationError,
    ROOT,
    get_inject_at,
)


class TestAuthorization(TestCase):
    def test_is_valid_for_timestamp(self):
        authorization = Authorization(
            None,
            frozenset("root"),
            datetime.fromisoformat("2022-01-01"),
            datetime.fromisoformat("2022-02-01"),
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-01-02"))
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-01-01"))
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-02-01"))
        )
        self.assertFalse(
            authorization.is_valid_for_timestamp(
                datetime.fromisoformat("2022-02-01 00:00:01")
            )
        )
        self.assertFalse(
            authorization.is_valid_for_timestamp(
                datetime.fromisoformat("2021-12-31 23:59:59")
            )
        )

    def test_is_valid_for_timestamp_no_min(self):
        authorization = Authorization(
            None, frozenset("root"), None, datetime.fromisoformat("2022-02-01")
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-01-01"))
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-02-01"))
        )
        self.assertFalse(
            authorization.is_valid_for_timestamp(
                datetime.fromisoformat("2022-02-01 00:00:01")
            )
        )

    def test_is_valid_for_timestamp_no_max(self):
        authorization = Authorization(
            None, frozenset("root"), datetime.fromisoformat("2022-02-01"), None
        )
        self.assertFalse(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-01-01"))
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-02-01"))
        )
        self.assertTrue(
            authorization.is_valid_for_timestamp(
                datetime.fromisoformat("2022-02-01 00:00:01")
            )
        )

    def test_is_valid_for_timestamp_no_timestamp(self):
        authorization = Authorization(None, frozenset("root"), None, None)
        self.assertTrue(
            authorization.is_valid_for_timestamp(datetime.fromisoformat("2022-02-01"))
        )

    def test_is_valid_for_timestamp_now(self):
        a_day = relativedelta(days=1)
        authorization = Authorization(
            None,
            frozenset("root"),
            datetime.now() - a_day,
            datetime.now() + a_day,
        )
        self.assertTrue(authorization.is_valid_for_timestamp())

    def test_has_scope(self):
        authorization = Authorization(None, frozenset(["foo", "bar"]), None, None)
        self.assertTrue(authorization.has_scope("foo"))
        self.assertFalse(authorization.has_scope("zap"))

    def test_has_any_scope(self):
        authorization = Authorization(None, frozenset(["foo", "bar"]), None, None)
        self.assertTrue(authorization.has_any_scope({"foo"}))
        self.assertFalse(authorization.has_any_scope({"zap"}))
        self.assertTrue(authorization.has_any_scope({"foo", "zap"}))

    def test_has_all_scope(self):
        authorization = Authorization(None, frozenset(["foo", "bar"]), None, None)
        self.assertTrue(authorization.has_all_scopes({"foo"}))
        self.assertTrue(authorization.has_all_scopes({"foo", "bar"}))
        self.assertFalse(authorization.has_all_scopes({"zap"}))
        self.assertFalse(authorization.has_all_scopes({"foo", "zap"}))

    def test_check_valid_for_timestamp(self):
        authorization = Authorization(
            None,
            frozenset("root"),
            datetime.fromisoformat("2022-01-01"),
            datetime.fromisoformat("2022-02-01"),
        )
        authorization.check_valid_for_timestamp(datetime.fromisoformat("2022-01-02"))
        authorization.check_valid_for_timestamp(datetime.fromisoformat("2022-01-01"))
        authorization.check_valid_for_timestamp(datetime.fromisoformat("2022-02-01"))
        with self.assertRaises(AuthorizationError):
            authorization.check_valid_for_timestamp(
                datetime.fromisoformat("2022-02-01 00:00:01")
            )
        with self.assertRaises(AuthorizationError):
            authorization.check_valid_for_timestamp(
                datetime.fromisoformat("2021-12-31 23:59:59")
            )

    def test_check_scope(self):
        authorization = Authorization(None, frozenset(["foo", "bar"]), None, None)
        authorization.check_scope("foo")
        with self.assertRaises(AuthorizationError):
            self.assertFalse(authorization.check_scope("zap"))

    def test_check_any_scope(self):
        authorization = Authorization(None, frozenset(["foo", "bar"]), None, None)
        authorization.check_any_scope({"foo"})
        with self.assertRaises(AuthorizationError):
            authorization.check_any_scope({"zap"})
        authorization.check_any_scope({"foo", "zap"})

    def test_check_all_scope(self):
        authorization = Authorization(None, frozenset(["foo", "bar"]), None, None)
        authorization.check_all_scopes({"foo"})
        authorization.check_all_scopes({"foo", "bar"})
        with self.assertRaises(AuthorizationError):
            authorization.check_all_scopes({"foo", "zap"})

    def test_get_inject_at(self):
        # noinspection PyUnusedLocal
        def foo(bar: str, auth: Authorization) -> str:
            return f"bar:{bar}, auth:{auth}"

        foo("bar", ROOT)  # Nonsense
        self.assertEqual("auth", get_inject_at(foo))
