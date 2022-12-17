# Servey - A Flexible Action Framework For Python

This project specifying metadata for python functions (In a manner similar to FastAPI) which is then used to
build REST, GraphQL, and Scheduled services. These are locally runnable / runnable in a hosted environment using
Starlette, Strawberry and Celery. They may also be run on AWS infrastructure using Serverless and Lambda. Tests and
examples may also be specified for **actions**. General design goals are:

* We want to cover the basic utility that almost any application will require as simply as possible.
* Convention over configuration
* Configurability
* Openness and playing nicely with the other children - not just doing something, but exposing details of what is being
  done to external services
* We want the utility offered by things like AWS while being as minimally tied to them as possible.

## Example

Install servey in your project using:

`pip install servey[server]`

Create a file *actions.py* containing the following:

```
from servey.action.action import action
from servey.trigger.web_trigger import WEB_GET


@action(triggers=(WEB_GET,))
def say_hello(name: str) -> str:
    """ Greet a user! """
    return f"Hello {name}!"

```

### Note 

* The [action](servey/action/action.py) decorator indicates that the *say_hello* function will be special!
* The *actions* module (and any submodules of it) is the default location in which Servey will look for actions, though
this may be overridden by specifying a different value in the *SERVEY_ACTION_PATH* environment variable
* We specify a trigger for this action - *WEB_GET*. Different triggers may be specified for your action.
* Marshalling of arbitrary python objects is handled using [marshy](https://github.com/tofarr/marshy)
* Json Schema validation for arbitrary python objects is handled using [schemey](https://github.com/tofarr/schemey)

### Run

Start the starlette server using:

`python -m servey`

You should see console output regarding keys and temporary passwords (More on this in the Authorization section), as
well as information indicating that Uvicorn is running on port 8000 (This can be overriden with the *SERVER_PORT*
environment variable). 

The following endpoints are set up by default:

* http://localhost:8000/docs : OpenAPI Docs for your project
* http://localhost:8000/graphiql/ : GraphQL debugger for your project
* http://localhost:8000/openapi.json : OpenAPI Schema for your project
* http://localhost:8000/graphql : GraphQL endpoint for your project

Note that the OpenAPI Docs are populated using the annotations on your function,
the action decorator, and any documentation you provided.

## Specifying Example Usage for Actions

Examples for usage may be specified in the [action](servey/action/action.py)
decorator, and will be available in the OpenAPI schema as well as potentially
being used to generate unit tests. Update your actions.py with the following:

```
from servey.action.action import action
from servey.action.example import Example
from servey.trigger.web_trigger import WEB_GET


@action(
    triggers=(WEB_GET,),
    examples=(
        Example(
            name='greet_developer',
            description='Say hello to the developer',
            params={'name': 'Developer'},
            result='Hello Developer!'
        ),
    )
)
def say_hello(name: str) -> str:
    """ Greet a user! """
    return f"Hello {name}!"

```

Restart the server, and your OpenAPI schema will have been updated
with the example you provided!

Run `pip install pytest`, add an empty `tests/__init__.py` and then
specify the following `tests/test_actions.py`:

```
from servey.servey_test.test_servey_actions import define_test_class

TestActions = define_test_class()
```

* Run tests with `python -m unittest discover -s tests`
* TestActions will include tests of all your examples from your
  actions where *include_in_tests* is True
* Nothing prevents you from creating your own unit tests
  for actions - they're just functions with an addtional
  *__servey_action__* attribute!

## Caching

Actions should be able to provide hints to clients about what sort of caching strategy is recommended. (The clients
can ignore this of course!) Http caching available for REST endpoints, but not GraphQL - though technologies like
React Query could be used to add it. Consider the following *actions.py*:

```
from datetime import datetime
from time import sleep

from servey.action.action import action
from servey.cache_control.ttl_cache_control import TtlCacheControl
from servey.trigger.web_trigger import WEB_POST


@action(triggers=(WEB_POST,), cache_control=TtlCacheControl(30))
def slow_get_with_ttl() -> datetime:
    """
    This function demonstrates http caching with a slow function. The function will take 3 seconds to return, but
    the client should cache the results for 30 seconds.
    """
    sleep(3)
    return datetime.now()

```

Notice that when you restart the server and run this from the OpenAPI test page, the first time it runs it should
take ~3 seconds. Subsequent runs are instant as the disk cache to holds the result for 30 seconds.

## Authorization

Servey Provides a pluggable authorization mechanism. By default, Servey uses JWT tokens and scopes for authorization,
with a key for generating them either specified in the **JWT_SECRET_KEY** environment variable or regenerated on each
server restart. (The AWS Lambda implementation uses KMS by default for key storage.) Note that we are talking about 
**Authorization** here rather than **Authentication**. 

Servey does not want to specify *how* a valid token should be issued,
though we do include [debug authenticator implementation](servey/servey_starlette/route_factory/authenticator_route_factory.py)
based on OAuth2. It generates a random password which is printed to the logs on server restart. 
Alternatively you may specify a password in the *SERVEY_DEBUG_AUTHENTICATOR_PASSWORD* environment variable.
A *REAL* Authenticator would be backed by a database of some kind, and could be plugged in to replace this one,
or even run from a different server.

Actions may specify an *access_control* to limit access. Consider the following *actions.py*:

```
from typing import Optional

from servey.action.action import action
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import Authorization
from servey.trigger.web_trigger import WEB_GET


@action(triggers=(WEB_GET,))
def echo_authorization(
    authorization: Optional[Authorization],
) -> Optional[Authorization]:
    """
    By default, authorization is derived from signed http headers - this just serves as a way
    of returning this info
    """
    return authorization


@action(triggers=(WEB_GET,), access_control=ScopeAccessControl(execute_scope='root'))
def only_for_root() -> str:
    """
    This can only be executed if the user has the root scope
    """
    return 'Some Secret Data!'

```

* The OpenAPI docs page now includes an OAuth2 section.
* **echo_authorization** gets the authorization from the http headers, decodes and confirms it and echos it. By default,
  we look for parameters with type Authorization and inject them from the context rather than directly from input parameters.
* **only_for_root** can only be executed by users with the root scope

## Scheduler

TODO: Document

## Resolvers

TODO: Document

## AWS

TODO: Document

## Deploying new versions of this Servey to Pypi

```
pip install setuptools wheel
python setup.py sdist bdist_wheel
pip install twine
python -m twine upload dist/*
```