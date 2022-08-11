from servey.action import action


@action
def greet(name: str) -> str:
    return f"Hello {name}"
