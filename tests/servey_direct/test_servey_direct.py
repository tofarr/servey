from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.servey_direct.__main__ import main


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
                "servey.servey_direct.__main__.find_actions",
                return_value=[get_action(my_action)],
            ),
        ):
            main()
        self.assertTrue(was_run)

    def test_servey_direct_no_action(self):
        @action
        def my_action() -> str:
            """Dummy"""

        with (
            patch("sys.argv", ["servey", "--run=action", "--action=does_not_exist"]),
            patch(
                "servey.servey_direct.__main__.find_actions",
                return_value=[get_action(my_action)],
            ),
        ):
            with self.assertRaises(ValueError):
                main()
