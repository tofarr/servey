from unittest import TestCase

from servey.action.batch_invoker import noop


class TestBatchInvoker(TestCase):
    def test_noop(self):
        item = "foobar"
        self.assertEqual([item], noop(item))
