from typing import Dict

from celery import Celery

from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.servey_celery.celery_config.celery_config_abc import CeleryConfigABC
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


class FixedRateTriggerConfig(CeleryConfigABC):
    def configure(self, app: Celery, global_ns: Dict):
        has_triggers = False
        for _action, _ in find_actions_with_trigger_type(FixedRateTrigger):
            if _action.name not in global_ns:
                global_ns[_action.name] = app.task(_action.fn)
                has_triggers = True

        if not has_triggers:
            return

        # noinspection PyUnusedLocal
        @app.on_after_configure.connect
        def setup_periodic_tasks(sender, **kwargs):
            for action, trigger in find_actions_with_trigger_type(FixedRateTrigger):
                task = global_ns[action.name]
                sender.add_periodic_task(trigger.interval, task.s())
