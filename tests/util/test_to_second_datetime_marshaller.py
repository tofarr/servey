from datetime import datetime, timezone
from unittest import TestCase

from servey.util.to_second_datetime_marshaller import ToSecondDatetimeMarshaller


class TestToSecondDatetimeMarshaller(TestCase):
    def test_load_and_dump(self):
        time = datetime(2022, 12, 1, 11, 43, 26, tzinfo=timezone.utc)
        marshaller = ToSecondDatetimeMarshaller()
        dumped = marshaller.dump(time)
        self.assertEqual("2022-12-01T11:43:26+00:00", dumped)
        loaded = marshaller.load(dumped)
        self.assertEqual(time, loaded)

    def test_dump_microseconds(self):
        time = datetime(2020, 2, 3, 4, 5, 6, microsecond=503, tzinfo=timezone.utc)
        marshaller = ToSecondDatetimeMarshaller()
        dumped = marshaller.dump(time)
        self.assertEqual("2020-02-03T04:05:06+00:00", dumped)
