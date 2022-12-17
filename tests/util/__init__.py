from unittest import TestCase

from servey.util import to_snake_case, secure_hash


class TestUtil(TestCase):
    def test_to_snake_case(self):
        self.assertEqual("foo_bar", to_snake_case("FooBar"))
        self.assertEqual("foo_bar", to_snake_case("fooBar"))

    def test_secure_hash(self):
        # noinspection SpellCheckingInspection
        self.assertEqual(
            "dcyqBpChAxfvEaF0tCGA9wEuNzeraehnLDpwJsiHYYs=",
            secure_hash(dict(foo=["bar", 10, True, None])),
        )
        # noinspection SpellCheckingInspection
        self.assertEqual(
            "1ytSS9/4lLZ8kCq02RB8DQMF7yB1vlLugKQDRcXwdQE=",
            secure_hash(dict(foo=["bar", 10, False, None])),
        )
