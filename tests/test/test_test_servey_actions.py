from unittest import TestCase
from unittest.mock import patch
from servey.finder.found_action import FoundAction


class TestTestServeyActions(TestCase):

    def test_define_test_class(self):
        with patch('servey.action.finder.action_finder_abc.find_actions', return_value=[
            FoundAction()
        ])