from unittest import TestCase

from servey.util import to_snake_case, secure_hash, entity_to_camel_case


class TestUtil(TestCase):
    def test_to_snake_case(self):
        self.assertEqual("foo_bar", to_snake_case("FooBar"))
        self.assertEqual("foo_bar", to_snake_case("fooBar"))

    def test_attr_to_camel_case(self):
        self.assertEqual("FooBar", entity_to_camel_case("foo_bar"))
        self.assertEqual("Foo", entity_to_camel_case("foo"))

    def test_entity_camel_case(self):
        self.assertEqual("FooBar", entity_to_camel_case("foo_bar"))
        self.assertEqual("Foo", entity_to_camel_case("foo"))

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
