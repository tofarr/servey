from dataclasses import dataclass, field
from typing import Optional, Iterator, Type, Tuple, Dict, TypeVar

from marshy.factory.impl_marshaller_factory import get_impls

from servey.action import Action
from servey.action_finder.action_finder_abc import ActionFinderABC

T = TypeVar("T")
_default_context = None


@dataclass
class ActionContext:
    """
    Repository for actions. These actions may then be mounted using aws lambda and API gateway
    (via serverless), using FastAPI, Celery, or through some other means.
    """

    actions: Dict[str, Action] = field(default_factory=dict)

    def get_action_by_name(self, name: str) -> Optional[Action]:
        return self.actions.get(name)

    def get_actions(self) -> Iterator[Action]:
        return iter(self.actions.values())

    def get_actions_with_trigger_type(
        self, trigger_type: Type[T]
    ) -> Iterator[Tuple[Action, T]]:
        for action in self.get_actions():
            for trigger in action.action_meta.triggers:
                if isinstance(trigger, trigger_type):
                    yield action, trigger


def get_default_action_context() -> ActionContext:
    global _default_context
    if not _default_context:
        _default_context = new_default_action_context()
    return _default_context


def new_default_action_context() -> ActionContext:
    finders = list(get_impls(ActionFinderABC))
    finders.sort(key=lambda f: f.priority)
    action_context = ActionContext()
    for finder in finders:
        for action in finder().find_actions():
            action_context.actions[action.action_meta.name] = action
    return action_context
