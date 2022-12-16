from unittest import TestCase
from unittest.mock import patch



class TestTestServeyActions(TestCase):

    def test_define_test_class(self):
        with patch('servey.action.finder.action_finder_abc.find_actions', return_value=[
            Action()
        ])