import logging

from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

from servey.action.marshallers.to_second_datetime_marshaller import (
    ToSecondDatetimeMarshaller,
)
from servey.servey_aws.event_parser.factory.appsync_event_parser_factory import (
    AppsyncEventParserFactory,
)

priority = 100
LOGGER = logging.getLogger(__name__)


def configure(context: MarshallerContext):
    from marshy.factory.dataclass_marshaller_factory import DataclassMarshallerFactory

    context.register_factory(
        DataclassMarshallerFactory(priority=101, exclude_dumped_values=tuple())
    )
    context.register_marshaller(ToSecondDatetimeMarshaller())
    configure_action_finder(context)
    configure_auth(context)
    configure_starlette(context)
    configure_aws(context)
    configure_serverless(context)
    configure_strawberry(context)
    configure_strawberry_starlette(context)


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
    from servey.servey_starlette.request_parser.factory.authorizing_parser_factory import (
        AuthorizingParserFactory,
    )
    from servey.servey_starlette.request_parser.factory.body_parser_factory import (
        BodyParserFactory,
    )
    from servey.servey_starlette.request_parser.factory.query_string_parser_factory import (
        QueryStringParserFactory,
    )
    from servey.servey_starlette.request_parser.factory.request_parser_factory_abc import (
        RequestParserFactoryABC,
    )

    register_impl(RequestParserFactoryABC, AuthorizingParserFactory, context)
    register_impl(RequestParserFactoryABC, BodyParserFactory, context)
    register_impl(RequestParserFactoryABC, QueryStringParserFactory, context)


def configure_starlette_response_render(context: MarshallerContext):
    from servey.servey_starlette.response_render.factory.body_render_factory import (
        BodyRenderFactory,
    )
    from servey.servey_starlette.response_render.factory.response_render_factory_abc import (
        ResponseRenderFactoryABC,
    )

    register_impl(ResponseRenderFactoryABC, BodyRenderFactory, context)


def configure_starlette_route_factory(context: MarshallerContext):
    from servey.servey_starlette.route_factory.action_route_factory import (
        ActionRouteFactory,
    )
    from servey.servey_starlette.route_factory.authenticator_route_factory import (
        AuthenticatorRouteFactory,
    )
    from servey.servey_starlette.route_factory.openapi_route_factory import (
        OpenapiRouteFactory,
    )
    from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC

    register_impl(RouteFactoryABC, ActionRouteFactory, context)
    register_impl(RouteFactoryABC, AuthenticatorRouteFactory, context)
    register_impl(RouteFactoryABC, OpenapiRouteFactory, context)


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

    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("Strawberry Module not found: skipping")
        return


def configure_strawberry_starlette(context: MarshallerContext):
    try:
        from servey.servey_starlette.route_factory.route_factory_abc import (
            RouteFactoryABC,
        )
        from servey.servey_strawberry.strawberry_starlette_route_factory import (
            StrawberryStarletteRouteFactory,
        )

        register_impl(RouteFactoryABC, StrawberryStarletteRouteFactory, context)

    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("Strawberry Module not found: skipping")
        return


def configure_aws(context: MarshallerContext):
    try:
        from servey.servey_aws.authorizer.kms_authorizer_factory import (
            KmsAuthorizerFactory,
        )
        from servey.security.authorizer.authorizer_factory_abc import (
            AuthorizerFactoryABC,
        )

        register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory, context)

        from servey.servey_aws.event_parser.factory.event_parser_factory import (
            EventParserFactory,
        )
        from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
            EventParserFactoryABC,
        )
        from servey.servey_aws.event_parser.factory.api_gateway_event_parser_factory import (
            ApiGatewayEventParserFactory,
        )

        register_impl(EventParserFactoryABC, EventParserFactory, context)
        register_impl(EventParserFactoryABC, ApiGatewayEventParserFactory, context)
        register_impl(EventParserFactoryABC, AppsyncEventParserFactory, context)

        from servey.servey_aws.result_render.factory.result_render_factory import (
            ResultRenderFactory,
        )
        from servey.servey_aws.result_render.factory.result_render_factory_abc import (
            ResultRenderFactoryABC,
        )
        from servey.servey_aws.result_render.factory.api_gateway_result_render_factory import (
            ApiGatewayResultRenderFactory,
        )

        register_impl(ResultRenderFactoryABC, ResultRenderFactory, context)
        register_impl(ResultRenderFactoryABC, ApiGatewayResultRenderFactory, context)

    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("AWS module not found: skipping")


def configure_serverless(context: MarshallerContext):
    try:
        from servey.servey_aws.serverless.yml_config.yml_config_abc import YmlConfigABC
        from servey.servey_aws.serverless.yml_config.action_function_config import (
            ActionFunctionConfig,
        )
        from servey.servey_aws.serverless.yml_config.appsync_config import AppsyncConfig
        from servey.servey_aws.serverless.yml_config.kms_key_config import KmsKeyConfig

        register_impl(YmlConfigABC, ActionFunctionConfig, context)
        register_impl(YmlConfigABC, AppsyncConfig, context)
        register_impl(YmlConfigABC, KmsKeyConfig, context)

        from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
            TriggerHandlerABC,
        )
        from servey.servey_aws.serverless.trigger_handler.web_trigger_handler import (
            WebTriggerHandler,
        )
        from servey.servey_aws.serverless.trigger_handler.fixed_rate_trigger_handler import (
            FixedRateTriggerHandler,
        )

        register_impl(TriggerHandlerABC, WebTriggerHandler, context)
        register_impl(TriggerHandlerABC, FixedRateTriggerHandler, context)

    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("Serverless module not found: skipping")
