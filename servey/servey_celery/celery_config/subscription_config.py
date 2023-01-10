from typing import Dict

from celery import Celery

from servey.finder.subscription_finder_abc import find_subscriptions
from servey.servey_celery.celery_config.celery_config_abc import CeleryConfigABC


class SubscriptionConfig(CeleryConfigABC):
    def configure(self, app: Celery, global_ns: Dict):
        for _subscription in find_subscriptions():
            if _subscription.action_subscribers:
                for _action in _subscription.action_subscribers:
                    if _action.name not in global_ns:
                        global_ns[_action.name] = app.task(_action.fn)
