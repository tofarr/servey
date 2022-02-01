from servey.meta.service_meta import ServiceMeta
from servey.servey_context import ServeyContext
from servey.wrapper import find_actions, find_publishers, wrap_action

priority = 100
ACTIONS_PATH = 'actions'
PUBLISHERS_PATH = 'publishers'


def configure_servey(context: ServeyContext):
    """
    @wrap_action(name='')
    def meta() -> ServiceMeta:
        action_meta = [a.get_meta() for a in context.actions_by_name.values()]
        publisher_meta = [p.get_meta() for p in context.publishers_by_name.values()]
        connector_meta = context.connector.get_meta() if context.connector else None
        service_meta = ServiceMeta(context.name, context.description, action_meta, publisher_meta, connector_meta)
        return service_meta

    context.actions_by_name['get_json_schema'] = meta.__action__
    """
    for action in find_actions(ACTIONS_PATH):
        context.actions_by_name[action.name] = action
    for publisher in find_publishers(PUBLISHERS_PATH):
        context.publishers_by_name[publisher.name] = publisher
