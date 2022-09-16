import logging

from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

priority = 100
LOGGER = logging.getLogger(__name__)


def configure(context: MarshallerContext):
    configure_action_finder(context)
    configure_auth(context)
    configure_starlette(context)
    #configure_aws(context)
    #configure_strawberry(context)


def configure_action_finder(context: MarshallerContext):
    from servey.action.finder.action_finder_abc import ActionFinderABC
    from servey.action.finder.module_action_finder import ModuleActionFinder
    register_impl(ActionFinderABC, ModuleActionFinder, context)


def configure_auth(context: MarshallerContext):
    from servey.security.authorizer.authorizer_factory_abc import AuthorizerFactoryABC
    from servey.security.authorizer.jwt_authorizer_factory import JwtAuthorizerFactory
    register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory, context)


def configure_starlette(context: MarshallerContext):
    try:
        configure_starlette_request_parser(context)
        configure_starlette_response_render(context)
        configure_starlette_route_factory(context)
    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("Starlette not installed - Skipping")


def configure_starlette_request_parser(context: MarshallerContext):
    from servey.servey_starlette.request_parser.factory.authorizing_parser_factory import AuthorizingParserFactory
    from servey.servey_starlette.request_parser.factory.body_parser_factory import BodyParserFactory
    from servey.servey_starlette.request_parser.factory.query_string_parser_factory import QueryStringParserFactory
    from servey.servey_starlette.request_parser.factory.request_parser_factory_abc import RequestParserFactoryABC
    from servey.servey_starlette.request_parser.factory.self_parser_factory import SelfParserFactory

    register_impl(RequestParserFactoryABC, AuthorizingParserFactory, context)
    register_impl(RequestParserFactoryABC, BodyParserFactory, context)
    register_impl(RequestParserFactoryABC, QueryStringParserFactory, context)
    register_impl(RequestParserFactoryABC, SelfParserFactory, context)


def configure_starlette_response_render(context: MarshallerContext):
    from servey.servey_starlette.response_render.factory.body_render_factory import BodyRenderFactory
    from servey.servey_starlette.response_render.factory.response_render_factory_abc import ResponseRenderFactoryABC
    register_impl(ResponseRenderFactoryABC, BodyRenderFactory, context)


def configure_starlette_route_factory(context: MarshallerContext):
    from servey.servey_starlette.route_factory.action_route_factory import ActionRouteFactory
    from servey.servey_starlette.route_factory.authenticator_route_factory import AuthenticatorRouteFactory
    from servey.servey_starlette.route_factory.openapi_route_factory import OpenapiRouteFactory
    from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC
    register_impl(RouteFactoryABC, ActionRouteFactory, context)
    register_impl(RouteFactoryABC, AuthenticatorRouteFactory, context)
    register_impl(RouteFactoryABC, OpenapiRouteFactory, context)


"""
def configure_strawberry(context: MarshallerContext):
    try:
        from servey.servey_strawberry.handler_filter.handler_filter_abc import (
            HandlerFilterABC,
        )
        from servey.servey_strawberry.handler_filter.authorization_handler_filter import (
            AuthorizationHandlerFilter,
        )
        from servey.servey_strawberry.handler_filter.strawberry_type_handler_filter import (
            StrawberryTypeHandlerFilter,
        )

        from servey.servey_strawberry.entity_factory.entity_factory_abc import (
            EntityFactoryABC,
        )
        from servey.servey_strawberry.entity_factory.dataclass_factory import (
            DataclassFactory,
        )
        from servey.servey_strawberry.entity_factory.enum_factory import (
            EnumFactory,
        )
        from servey.servey_strawberry.entity_factory.forward_ref_factory import (
            ForwardRefFactory,
        )
        from servey.servey_strawberry.entity_factory.generic_factory import (
            GenericFactory,
        )
        from servey.servey_strawberry.entity_factory.no_op_factory import (
            NoOpFactory,
        )

        register_impl(HandlerFilterABC, AuthorizationHandlerFilter, context)
        register_impl(HandlerFilterABC, StrawberryTypeHandlerFilter, context)

        register_impl(EntityFactoryABC, DataclassFactory, context)
        register_impl(EntityFactoryABC, EnumFactory, context)
        register_impl(EntityFactoryABC, ForwardRefFactory, context)
        register_impl(EntityFactoryABC, GenericFactory, context)
        register_impl(EntityFactoryABC, NoOpFactory, context)
    except ModuleNotFoundError:
        LOGGER.info("Strawberry Module not found: skipping")


def configure_aws(context: MarshallerContext):
    try:
        from servey.servey_aws.kms_authorizer_factory import KmsAuthorizerFactory

        register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory, context)
    except ModuleNotFoundError:
        LOGGER.info("AWS Module not found: skipping")
"""
