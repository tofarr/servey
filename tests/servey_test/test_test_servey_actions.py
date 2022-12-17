from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.action.example import Example
from servey.servey_test.test_servey_actions import define_test_class


class TestTestServeyActions(TestCase):
    def test_define_test_class(self):
        with patch(
            "servey.servey_test.test_servey_actions.find_actions",
            return_value=[get_action(say_hello)],
        ):
            # noinspection PyPep8Naming
            TestClass = define_test_class()
            self.assertEqual("TestServeyActions", TestClass.__name__)
            self.assertTrue(issubclass(TestClass, TestCase))
            keys = {k for k in TestClass.__dict__.keys() if not k.startswith("__")}
            self.assertEqual({"test_say_hello__world", "test_say_hello__bad"}, keys)
            test_instance = TestClass()
            test_instance.test_say_hello__world()
            with self.assertRaises(AssertionError):
                # This example should fail!
                test_instance.test_say_hello__bad()


@action(
    examples=(
        Example("world", params=dict(name="World"), result="Hello World!"),
        Example("bad", params=dict(name="Wrong"), result="Nope"),
    )
)
def say_hello(name: str) -> str:
    return f"Hello {name}!"
