from typing import Tuple, Iterator

from marshy.types import ExternalItemType

from servey.action_finder import FoundAction

ALSO MOUNT AN API ENDPOINT

@dataclass
class ServerlessYmlMount:
    """ Mechanism for mounting actions by including them in a serverless YAML for deployment to AWS. """
    serverless_event_factories: Optional[List[ServerlessEventFactoryABC]]

    def __post_init__(self):
        # Read YML

    def mount_actions(self, found_actions: Iterator[FoundAction]):
        pass

    def actions_to_serverless_functions(self, found_actions: Iterator[FoundAction]) -> ExternalItemType:
        pass

    def action_to_serverless_function(self, found_action: FoundAction) -> Tuple[str, ExternalItemType]:
        action = found_action.action
        action_meta = action.action_meta
        fn = {
            'handler': found_action.module.__name__.replace('.', '/') + '.' + action.fn.__name__,
            'timeout': action_meta.timeout
        }
        events = []
        marshaller
        add_api_gateway_event(trigger)
        add_fixed_rate_event()
        if events:
            fn['events'] = events
        return action_meta.name, fn
