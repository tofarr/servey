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
from servey.integration.fastapi_integration.handler_filter.authorization_handler_filter import (
    AuthorizationHandlerFilter,
)
from servey.integration.fastapi_integration.handler_filter.body_handler_filter import (
    BodyHandlerFilter,
)
from servey.integration.fastapi_integration.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
)

priority = 100


def configure(context: MarshallerContext):
    register_impl(ActionFinderABC, ModuleActionFinder, context)
    register_impl(AuthenticatorFactoryABC, LocalAuthenticatorFactory, context)
    register_impl(AuthenticatorFactoryABC, RemoteAuthenticatorFactory, context)
    register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory, context)
    register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory, context)

    register_impl(HandlerFilterABC, AuthorizationHandlerFilter, context)
    register_impl(HandlerFilterABC, BodyHandlerFilter, context)
    """
    register_impl(EntityFactoryABC, DataclassFactory, context)
    register_impl(EntityFactoryABC, EnumFactory, context)
    register_impl(EntityFactoryABC, ForwardRefFactory, context)
    register_impl(EntityFactoryABC, GenericFactory, context)
    register_impl(EntityFactoryABC, PrimitiveFactory, context)
    """
