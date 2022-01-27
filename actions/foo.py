from servey.http_method import HttpMethod
from servey.wrapper import wrap_action


@wrap_action
def get_hello(name: str) -> str:
    """ Say hello! """
    return f'Hello {name}'


@wrap_action(http_methods=(HttpMethod.POST,))
def post_hello(name: str) -> str:
    """ Say hello using a post request! """
    return f'Hello {name}'
