from datetime import datetime

from servey.action.action import action
from servey.trigger.fixed_rate_trigger import FixedRateTrigger
from servey.trigger.web_trigger import WEB_GET
from tests.specs.number_spec.models import IntegerStats


@action(triggers=(WEB_GET,))
def integer_stats(value: int) -> IntegerStats:
    return IntegerStats(value)


@action
def integer_stats_consumer(stats: IntegerStats):
    print(f"IntegerStats: {stats.value}: Factorial: {stats.factorial}")


@action(triggers=(FixedRateTrigger(300),))
def integer_stats_publisher():
    integer_stats_ = IntegerStats(int(datetime.now().timestamp()) % 200)
    from tests.specs.number_spec.subscriptions import integer_stats_queue

    integer_stats_queue.publish(integer_stats_)
