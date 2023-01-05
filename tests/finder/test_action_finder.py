import os
from unittest import TestCase
from unittest.mock import patch

from servey.finder.action_finder_abc import find_actions


class TestActionFinder(TestCase):
    def test_find_actions(self):
        with patch.dict(os.environ, {"SERVEY_MAIN": "tests.finder"}):
            action_ = next(a for a in find_actions() if a.name == "marco")
            self.assertEqual("Polo!", action_.fn())
