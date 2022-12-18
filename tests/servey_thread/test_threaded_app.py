from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import get_action, action
from servey.servey_thread.fixed_rate_trigger_thread import FixedRateTriggerThread
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


class TestThreadedApp(TestCase):
    def test_threaded(self):
        print_time()
        print_time_action = get_action(print_time)
        with (
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[print_time_action],
            ),
            patch(
                "servey.servey_thread.fixed_rate_trigger_thread.FixedRateTriggerThread.start",
                return_value=None,
            ),
        ):
            import servey.servey_thread.__main__ as thread_main

            self.assertEqual(1, len(thread_main._THREADS))

    def test_run(self):
        def raise_error():
            assert False

        def do_not_sleep(_: int):
            """Speed up iteration"""

        thread = FixedRateTriggerThread(raise_error, FixedRateTrigger(1), False)
        with patch("time.sleep", do_not_sleep):
            with self.assertRaises(AssertionError):
                thread.run()


# noinspection PyTypeChecker
@action(triggers=(FixedRateTrigger(10),))
def print_time() -> type(None):
    print(f"Time is : {datetime.now()}")
