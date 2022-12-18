import importlib
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action


class TestServeyDirect(TestCase):
    def test_servey_direct(self):
        was_run = False

        @action
        def my_action() -> str:
            nonlocal was_run
            was_run = True
            return "Action was run"

        with (
            patch("sys.argv", ["servey", "--run=action", "--action=my_action"]),
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[get_action(my_action)],
            ),
        ):
            _reload_module()
        self.assertTrue(was_run)

    def test_servey_direct_no_action(self):
        @action
        def my_action() -> str:
            """Dummy"""

        with (
            patch("sys.argv", ["servey", "--run=action", "--action=does_not_exist"]),
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[get_action(my_action)],
            ),
        ):
            with self.assertRaises(ValueError):
                _reload_module()


_module = None


def _reload_module():
    global _module
    if _module:
        importlib.reload(_module)
    else:
        from servey.servey_direct import __main__

        _module = __main__
