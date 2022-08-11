from dataclasses import dataclass
from typing import Iterator, Optional

from fastapi import FastAPI

from servey.action import Action
from servey.action_finder import find_default_actions
from servey.trigger.web_trigger import WebTrigger


@dataclass
class FastapiMount:
    """ Utility for mounting actions to fastapi. """
    api: FastAPI
    path_pattern: str = '/actions/{action_name}'

    def mount_actions(self, actions: Iterator[Action]):
        for action in actions:
            self.mount_action(action)

    def mount_action(self, action: Action):
        web_trigger = _get_web_trigger(action)
        if not web_trigger:
            return
        path = self.path_pattern.format(action_name=action.action_meta.name)
        if web_trigger.is_mutation:
            wrapper = self.api.post(path)
        else:
            wrapper = self.api.get(path)
        wrapper(action.fn)


def _get_web_trigger(action: Action) -> Optional[WebTrigger]:
    trigger = next((t for t in action.action_meta.triggers if isinstance(t, WebTrigger)), None)
    return trigger
