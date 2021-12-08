from servey.action_type import ActionType
from servey.meta.service_meta import ServiceMeta, ServiceMeta
from servey.servey_context import ServeyContext
from servey.wrapper import find_actions, find_publishers, wrap_action

priority = 100
ACTIONS_PATH = 'actions'
PUBLISHERS_PATH = 'publishers'


def configure_servey(context: ServeyContext):

    @wrap_action(action_type=ActionType.GET, name='')
    def meta() -> ServiceMeta:
        action_meta = [a.get_meta() for a in context.actions_by_name.values()]
        service_meta = ServiceMeta(context.name, context.description, action_meta)
        return service_meta

    context.actions_by_name['get_json_schema'] = meta.__action__

    for action in find_actions(ACTIONS_PATH):
        context.actions_by_name[action.name] = action
    for publisher in find_publishers(PUBLISHERS_PATH):
        context.publishers_by_name[publisher.name] = publisher
