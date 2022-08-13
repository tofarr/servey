import asyncio
from logging import getLogger
from typing import Optional

from servey.action import Action
from servey.action_context import ActionContext, get_default_action_context
from servey.trigger.fixed_rate_trigger import FixedRateTrigger

LOGGER = getLogger(__name__)


def mount_all(action_context: Optional[ActionContext] = None):
    LOGGER.info('mount_all')
    if not action_context:
        action_context = get_default_action_context()
    for action, trigger in action_context.get_actions_with_trigger_type(FixedRateTrigger):
        mount_action(action, trigger)


def mount_action(action: Action, trigger: FixedRateTrigger):
    LOGGER.info(f'mount_action:{action.action_meta.name}')
    asyncio.create_task(fixed_rate_task(action, trigger))


async def fixed_rate_task(action: Action, trigger: FixedRateTrigger):
    while True:
        await asyncio.sleep(trigger.interval)
        action.invoke_async(trigger.authorization)
