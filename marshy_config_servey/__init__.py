from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

from servey.access_control.authorizer_factory_abc import AuthorizerFactoryABC
from servey.access_control.jwt_authorizer_factory import JwtAuthorizerFactory
from servey.action_finder.action_finder_abc import ActionFinderABC
from servey.action_finder.module_action_finder import ModuleActionFinder
from servey.integration.aws.kms_authorizer_factory import KmsAuthorizerFactory
from servey.integration.fastapi_integration.authenticator.factory.authenticator_factory_abc import (
    AuthenticatorFactoryABC,
)
from servey.integration.fastapi_integration.authenticator.factory.local_authenticator_factory import (
    LocalAuthenticatorFactory,
)
from servey.integration.fastapi_integration.authenticator.factory.remote_authenticator_factory import (
    RemoteAuthenticatorFactory,
)
from servey.integration.fastapi_integration.executor_factory.authorized_fastapi_handler_factory import (
    AuthorizedFastapiHandlerFactory,
)
from servey.integration.fastapi_integration.executor_factory.fastapi_handler_factory import (
    FastapiHandlerFactory,
)
from servey.integration.fastapi_integration.executor_factory.fastapi_handler_factory_abc import (
    FastapiHandlerFactoryABC,
)

priority = 100


def configure(context: MarshallerContext):
    register_impl(ActionFinderABC, ModuleActionFinder, context)
    register_impl(AuthenticatorFactoryABC, LocalAuthenticatorFactory, context)
    register_impl(AuthenticatorFactoryABC, RemoteAuthenticatorFactory, context)
    register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory, context)
    register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory, context)
    register_impl(FastapiHandlerFactoryABC, FastapiHandlerFactory, context)
    register_impl(FastapiHandlerFactoryABC, AuthorizedFastapiHandlerFactory, context)
