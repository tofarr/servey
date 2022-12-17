from datetime import datetime, timezone

from marshy.marshaller import DatetimeMarshaller


class ToSecondDatetimeMarshaller(DatetimeMarshaller):
    """
    Marshaller which does not dump microseconds - appropriate for server instances where this precision is
    not useful (And Appsync scalars don't support it)
    """

    def dump(self, item: datetime) -> str:
        dumped = item.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        return dumped
