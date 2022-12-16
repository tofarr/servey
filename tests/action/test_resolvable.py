from unittest import TestCase

from servey.action.resolvable import resolvable, get_resolvable
from servey.security.access_control.allow_all import ALLOW_ALL


class TestResolvable(TestCase):

    def test_decorator(self):
        res = get_resolvable(_dummy)
        self.assertEqual(_dummy, res.fn)
        self.assertEqual(ALLOW_ALL, res.access_control)


@resolvable
def _dummy():
    pass
