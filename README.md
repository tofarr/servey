# Servey - A Flexible Action Framework For Python

This project specifying metadata for python functions (In a manner similar to FastAPI) which is then used to
build REST, GraphQL, and Scheduled services. These are locally runnable / runnable in a hosted environment using
[Starlette](https://www.starlette.io/), [Strawberry](https://strawberry.rocks/) and [Celery](https://docs.celeryq.dev/).
They may also be run on AWS infrastructure using Serverless and Lambda. Tests and examples may also be specified for
**actions**. General design goals are:

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
* The *actions* module (and any submodules of it) is the default location in which Servey will look for actions.
  This may be overridden by specifying a different value in the *SERVEY_ACTION_PATH* environment variable
* We specify a trigger for this action - *WEB_GET*
* Servey uses [marshy](https://github.com/tofarr/marshy) to marshall arbitrary python objects.
* Servey uses [schemey](https://github.com/tofarr/schemey) for schema generation / validation.

### Run an action from the terminal

Actions should have unique names, which taken from the function name by default, but can also be overridden in the
decorator. This name can be used to run an action explicitly from the command line (or cron):

`python -m servey --run=action --action=say_hello "--event={\"name\": \"World\"}"`

### Run Server

Start the [Starlette](https://www.starlette.io/) server using:

`python -m servey`

You should see console output regarding keys and temporary passwords (More on this in the Authorization section), as
well as information indicating that [Uvicorn](https://www.uvicorn.org/) is running on port 8000. (You override this
using the *SERVER_PORT* environment variable)

The following endpoints deployed by default:

* http://localhost:8000/docs : OpenAPI Docs for your project
* http://localhost:8000/graphiql/ : GraphQL debugger for your project
* http://localhost:8000/openapi.json : OpenAPI Schema for your project
* http://localhost:8000/graphql : GraphQL endpoint for your project

Servey populates the OpenAPI Schema using the annotations on your function,
the action decorator, and any documentation you provided.

## Specifying Example Usage for Actions

You can specify action usage examples using the [action](servey/action/action.py) decorator.
These will be available in the OpenAPI schema as well as potentially being used to generate unit tests. Update your
actions.py with the following:

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

Restart the server, to update your OpenAPI schema.

Run `pip install pytest`, add an empty `tests/__init__.py` and then
specify the following `tests/test_actions.py`:

```
from servey.servey_test.test_servey_actions import define_test_class

TestActions = define_test_class()
```

* Run tests with `python -m unittest discover -s tests`
* TestActions will include tests of all your examples from your actions where *include_in_tests* is True
* Nothing prevents you from creating your own unit tests for actions - they're just functions with an additional
  *__servey_action__* attribute!

## Caching

Actions should be able to provide recommended caching strategies to clients. (The clients can ignore this of course!) 
Http caching available for REST endpoints, but not GraphQL - though technologies like
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
take ~3 seconds. Subsequent runs are instant as the disk cache retains the result for 30 seconds.

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
* GraphQL uses the same access_controllers, reading tokens from the Authorization http header. (Graphiql lets
  you specify this)

## Scheduler

So far we have demonstrated usage of [WebTrigger](servey/trigger/web_trigger.py), but triggers are pluggable and other
implementations are possible. One additional type included is the 
[FixedRateTrigger](servey/trigger/fixed_rate_trigger.py) This allows you to specify that a function should run at
regular intervals.

* In a single server / development environment, [Background Threads](servey/servey_thread/fixed_rate_trigger_thread.py)
  are used.
* If the environment specifies a *CELERY_BROKER*, Servey uses Celery to run background tasks in a distributed fashion
* In a Serverless / AWS lambda environment, servey implements scheduling by deploying triggers for the generated lambdas

[Here is a celery deployment example.](servey/servey_celery/celery_app.py)

## Nested Actions

Out of the box, actions may be defined on a function of a returned type, allowing for nested actions to be 
defined and resolved lazily in graphql. (Nested actions may have a WebTrigger too if required):

```
from dataclasses import dataclass

from servey.action.action import action
from servey.trigger.web_trigger import WEB_GET


@dataclass
class NumberStats:
    value: int

    @action
    async def factorial(self) -> int:
        """
        This demonstrates a resolvable field, lazily resolved (Usually by graphql)
        """
        result = 1
        index = self.value
        while index > 1:
            result *= index
            index -= 1
        return result


@action(
    triggers=(WEB_GET,),
)
def number_stats(value: int) -> NumberStats:
    return NumberStats(value)

```

* We define a return type NumberStats that is simply a python dataclass
* The field *factorial* is only resolved if requested in the graphql request
* Nested Actions may specify caching and access controls

## Subscriptions

Subscriptions model 2 particular use cases:

* Send updates to users browser when some event occurs
* Run some action when a particular event occurs
 
Servey finds [Subscriptions](servey/subscription/subscription.py) in the `subscriptions` module in a 
manner similar to how it finds actions. Subscriptions have a unique name used to identify them, and the 
`is_subscribable` flag determines whether the subscriptions allow external users to subscribe (Typically Via websocket).
Subscriptions may also be linked to a number of actions, and depending on the environment this may be a direct 
invocation, or via an event queue like celery or SQS. Servey also generates an
[asyncapi](https://www.asyncapi.com/docs) schema for your subscriptions at /asyncapi.json

When connecting, typically a subscriber provides a unique id to identify their connection. Events may be published to
a single subscriber (using their connection_id) or to all subscribed users (If no connection_id is supplied when 
publishing)

Create a `subscriptions.py` file with the following content:

```
from servey.subscription.subscription import subscription

messager = subscription(str, "messager")
```

Open your `actions.py` and add the following:

```
from servey.action.action import action
from subscriptions import messager

# noinspection PyUnusedLocal
@action(triggers=(WEB_POST,))
def broadcast_message(message: str, connection_id: Optional[str] = None) -> bool:
    """ Send a message to all connected users or to a single subscriber. """
    messager.publish(message, connection_id)
    return True
```

Restart the server, to go to https://localhost:8000/asyncapi.json

Unfortunately there is no studio where you can try it out with asyncapi like there is with OpenApi right now.
I have been using the "Browser WebSocket Client" chrome extension to test subscriptions Using the url:
ws://localhost:8000/subscription/messager/some_unique_subscriber_id) and the openapi docs to send messages.

You might have noticed that we use the terms `subscription` but do not actually implement graphql subscriptions. The
reason for this is we wanted to provide a unified interface for subscriptions across all platforms, and the way appsync
implements Graphql subscriptions is quite frankly, weird. (Each subscription is triggered by a mutation, there is no 
admin interface, you trigger the subscription by invoking the graphql mutation. Even if you can secure these, you
end up with mutations which are not useful to most users. And don't get me started on event filtering

type TriggerMessageEvent {
  subscriber_id: string
  event: Message
}

Mutation {
  triggerMessage(subscriber_id: string, event: Message): TriggerMessageEvent
}

Subscription {
  message(subscriber_id: string): TriggerMessageEvent
}

## AWS

Up until this point, we have mostly discussed development environments / deploying to a container. Servey also allows
your code to be deployed to AWS using Serverless. Servey will generate serverless definitions in yaml files in order to
facilitate this. We assume that you already have an aws account with appropriate access, and that you are set up
with serverless (You probably have a $HOME/.aws/credentials file set up). First, you'll need some extras to get this
working:

`pip install servey[serverless]`

Then you can regenerate your serverless.yml definitions using:

`python -m servey --run=sls`

* This will generate a new *serverless.yml* file for you if it is missing. (override environment variable
  *MAIN_SERVERLESS_YML_FILE* to choose a different name)
* Servey uses file includes to attempt to make the modifications to the main serverless yaml minimal.
* Actions get implemented as Lambdas - one per action.
* We implemented GraphQL using Appsync
* We implemented REST using API Gateway
* We implemented Authorizers using KMS
* We implements subscriptions to actions using SQS
* The generated lambdas as designed to allow direct invocation where the event contains unmarshalled parameters, or
  access by Appsync or API Gateway.
* Once you deploy your serverless project, you should be able to test from the Appsync, Api Gateway, and Lambda consoles
  respectively.

## Command line tools

Produce an openapi schema in `openapi.json`:

`python -m servey --run=openapi`

Produce a graphql schema in `servey_schema.graphql`:

`python -m servey --run=graphql-schema`

## Deploying new versions of this Servey to Pypi

```
pip install setuptools wheel
python setup.py sdist bdist_wheel
pip install twine
python -m twine upload dist/*
```