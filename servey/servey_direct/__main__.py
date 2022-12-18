"""
Allows invoking actions directly from the command line (Or via crontab)
Usage:

`python -m servey.servey_direct --action=ping`
`python -m servey.servey_direct --action=say_hello "--event={\"name\": \"Foobar\"}"`

"""
import argparse
import inspect
import json

from marshy import get_default_context

from servey.action.util import get_marshaller_for_params
from servey.finder.action_finder_abc import find_actions

parser = argparse.ArgumentParser(description="Invoke an action directly")
parser.add_argument("--run", default="action")
parser.add_argument("--action")
parser.add_argument("--event", default="{}")
args = parser.parse_args()


action = next((a for a in find_actions() if a.name == args.action), None)
if not action:
    raise ValueError(f"no_such_action:{args.action}")
marshaller = get_marshaller_for_params(action.fn, set())
kwargs = marshaller.load(json.loads(args.event))
result = action.fn(**kwargs)
return_annotation = inspect.signature(action.fn).return_annotation
if return_annotation != inspect.Parameter.empty:
    result = get_default_context().dump(result, return_annotation)
    result_str = json.dumps(result)
    print(result_str)
