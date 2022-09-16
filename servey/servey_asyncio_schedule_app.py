"""
App for case where servey is run in local schedule mode. Scheduled events are run using
asyncio (As opposed to Celery)
"""
import asyncio
from logging import getLogger

from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.finder.found_action import FoundAction
from servey.action.trigger.fixed_rate_trigger import FixedRateTrigger

LOGGER = getLogger(__name__)


async def fixed_rate_task(action_: FoundAction, trigger_: FixedRateTrigger):
    while True:
        await asyncio.sleep(trigger_.interval)
        loop = asyncio.get_event_loop()
        loop.call_soon(action_.fn)
        action_.fn()
        executor = action.create_executor()
        executor.execute_async()


for action, trigger in find_actions_with_trigger_type(FixedRateTrigger):
    asyncio.create_task(fixed_rate_task(action, trigger))
