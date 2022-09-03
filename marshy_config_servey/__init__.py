import logging

from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

from servey.access_control.authorizer_factory_abc import AuthorizerFactoryABC
from servey.action_finder.action_finder_abc import ActionFinderABC
from servey.action_finder.module_action_finder import ModuleActionFinder

priority = 100
LOGGER = logging.getLogger(__name__)


def configure(context: MarshallerContext):
    register_impl(ActionFinderABC, ModuleActionFinder, context)
    configure_auth(context)
    configure_starlette(context)
    configure_aws(context)
    configure_strawberry(context)


def configure_auth(context: MarshallerContext):
    from servey.access_control.jwt_authorizer_factory import JwtAuthorizerFactory

    register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory, context)


def configure_starlette(context: MarshallerContext):
    try:
        from servey.integration.starlette_integ.parser.parser_abc import (
            ParserFactoryABC,
        )
        from servey.integration.starlette_integ.parser.authorizing_parser import (
            AuthorizingParserFactory,
        )
        from servey.integration.starlette_integ.parser.body_parser import (
            BodyParserFactory,
        )
        from servey.integration.starlette_integ.parser.query_string_parser import (
            QueryStringParserFactory,
        )
        from servey.integration.starlette_integ.render.render_abc import (
            RenderFactoryABC,
        )
        from servey.integration.starlette_integ.render.body_render import (
            BodyRenderFactory,
        )
        from servey.integration.starlette_integ.route_factory.action_route_factory import (
            ActionRouteFactory,
        )
        from servey.integration.starlette_integ.route_factory.authenticator_route_factory import (
            AuthenticatorRouteFactory,
        )
        from servey.integration.starlette_integ.route_factory.openapi_route_factory import (
            OpenapiRouteFactory,
        )
        from servey.integration.starlette_integ.route_factory.route_factory_abc import (
            RouteFactoryABC,
        )
        from servey.integration.strawberry_integration.strawberry_starlette_route_factory import (
            StrawberryStarletteRouteFactory,
        )

        register_impl(ParserFactoryABC, AuthorizingParserFactory, context)
        register_impl(ParserFactoryABC, BodyParserFactory, context)
        register_impl(ParserFactoryABC, QueryStringParserFactory, context)
        register_impl(RenderFactoryABC, BodyRenderFactory, context)
        register_impl(RouteFactoryABC, ActionRouteFactory, context)
        register_impl(RouteFactoryABC, OpenapiRouteFactory, context)
        register_impl(RouteFactoryABC, AuthenticatorRouteFactory, context)
        register_impl(RouteFactoryABC, StrawberryStarletteRouteFactory, context)
    except ModuleNotFoundError:
        LOGGER.info("Starlette not installed - Skipping")


def configure_strawberry(context: MarshallerContext):
    try:
        from servey.integration.strawberry_integration.handler_filter.handler_filter_abc import (
            HandlerFilterABC,
        )
        from servey.integration.strawberry_integration.handler_filter.authorization_handler_filter import (
            AuthorizationHandlerFilter,
        )
        from servey.integration.strawberry_integration.handler_filter.strawberry_type_handler_filter import (
            StrawberryTypeHandlerFilter,
        )

        from servey.integration.strawberry_integration.entity_factory.entity_factory_abc import (
            EntityFactoryABC,
        )
        from servey.integration.strawberry_integration.entity_factory.dataclass_factory import (
            DataclassFactory,
        )
        from servey.integration.strawberry_integration.entity_factory.enum_factory import (
            EnumFactory,
        )
        from servey.integration.strawberry_integration.entity_factory.forward_ref_factory import (
            ForwardRefFactory,
        )
        from servey.integration.strawberry_integration.entity_factory.generic_factory import (
            GenericFactory,
        )
        from servey.integration.strawberry_integration.entity_factory.no_op_factory import (
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
        from servey.integration.aws.kms_authorizer_factory import KmsAuthorizerFactory

        register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory, context)
    except ModuleNotFoundError:
        LOGGER.info("AWS Module not found: skipping")
