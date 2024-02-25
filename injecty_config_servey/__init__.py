import logging

from injecty import InjectyContext
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.event_channel.background.background_invoker_abc import (
    BackgroundInvokerFactoryABC,
)
from servey.event_channel.websocket.websocket_sender import WebsocketSenderFactoryABC

priority = 90
LOGGER = logging.getLogger(__name__)


def configure(context: InjectyContext):
    from servey.util.to_second_datetime_marshaller import (
        ToSecondDatetimeMarshaller,
    )

    context.register_impl(MarshallerABC, ToSecondDatetimeMarshaller)
    configure_finders(context)
    configure_asyncio_invoker(context)
    configure_auth(context)
    configure_starlette(context)
    configure_aws(context)
    configure_serverless(context)
    configure_strawberry(context)
    configure_strawberry_starlette(context)
    configure_celery(context)
    configure_jinja2(context)


def configure_finders(context: InjectyContext):
    from servey.finder.action_finder_abc import ActionFinderABC
    from servey.finder.module_action_finder import ModuleActionFinder
    from servey.finder.module_event_channel_finder import ModuleEventChannelFinder
    from servey.finder.event_channel_finder_abc import EventChannelFinderABC

    context.register_impl(ActionFinderABC, ModuleActionFinder)
    context.register_impl(EventChannelFinderABC, ModuleEventChannelFinder)


def configure_asyncio_invoker(context: InjectyContext):
    from servey.servey_thread.asyncio_background_invoker import (
        AsyncioBackgroundInvokerFactory,
    )

    context.register_impl(BackgroundInvokerFactoryABC, AsyncioBackgroundInvokerFactory)


def configure_auth(context: InjectyContext):
    from servey.security.authorizer.authorizer_factory_abc import AuthorizerFactoryABC
    from servey.security.authorizer.jwt_authorizer_factory import JwtAuthorizerFactory
    from servey.security.authenticator.password_authenticator_abc import (
        PasswordAuthenticatorABC,
    )
    from servey.security.authenticator.root_password_authenticator import (
        RootPasswordAuthenticator,
    )

    context.register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory)
    context.register_impl(PasswordAuthenticatorABC, RootPasswordAuthenticator)


def configure_starlette(context: InjectyContext):
    try:
        configure_starlette_action_endpoint_factory(context)
        configure_starlette_route_factory(context)
        configure_starlette_middleware_factory(context)
    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_starlette_action_endpoint_factory(context: InjectyContext):
    from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
        ActionEndpointFactoryABC,
    )
    from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
        ActionEndpointFactory,
    )
    from servey.servey_starlette.action_endpoint.factory.authorizing_action_endpoint_factory import (
        AuthorizingActionEndpointFactory,
    )
    from servey.servey_starlette.action_endpoint.factory.caching_action_endpoint_factory import (
        CachingActionEndpointFactory,
    )
    from servey.servey_starlette.action_endpoint.factory.self_action_endpoint_factory import (
        SelfActionEndpointFactory,
    )

    context.register_impls(
        ActionEndpointFactoryABC,
        [
            ActionEndpointFactory,
            AuthorizingActionEndpointFactory,
            CachingActionEndpointFactory,
            SelfActionEndpointFactory,
        ],
    )


# noinspection DuplicatedCode
def configure_starlette_route_factory(context: InjectyContext):
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
    from servey.servey_starlette.route_factory.event_channel_route_factory import (
        EventChannelRouteFactory,
    )
    from servey.servey_starlette.route_factory.asyncapi_route_factory import (
        AsyncapiRouteFactory,
    )
    from servey.servey_starlette.route_factory.static_site_route_factory import (
        StaticSiteRouteFactory,
    )
    from servey.servey_starlette.event_channel.starlette_websocket_sender_factory import (
        StarletteWebsocketSenderFactory,
    )

    context.register_impls(
        RouteFactoryABC,
        [
            ActionRouteFactory,
            AuthenticatorRouteFactory,
            OpenapiRouteFactory,
            EventChannelRouteFactory,
            AsyncapiRouteFactory,
            StaticSiteRouteFactory,
        ],
    )

    context.register_impl(WebsocketSenderFactoryABC, StarletteWebsocketSenderFactory)


def configure_starlette_middleware_factory(context: InjectyContext):
    from servey.servey_starlette.middleware.middleware_factory_abc import (
        MiddlewareFactoryABC,
    )
    from servey.servey_starlette.middleware.cors_middleware_factory import (
        CORSMiddlewareFactory,
    )

    context.register_impl(MiddlewareFactoryABC, CORSMiddlewareFactory)


# noinspection DuplicatedCode
def configure_strawberry(context: InjectyContext):
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

        context.register_impls(
            HandlerFilterABC, [AuthorizationHandlerFilter, StrawberryTypeHandlerFilter]
        )

        context.register_impls(
            EntityFactoryABC,
            [
                DataclassFactory,
                EnumFactory,
                ForwardRefFactory,
                GenericFactory,
                NoOpFactory,
            ],
        )

    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_strawberry_starlette(context: InjectyContext):
    try:
        from servey.servey_starlette.route_factory.route_factory_abc import (
            RouteFactoryABC,
        )
        from servey.servey_strawberry.strawberry_starlette_route_factory import (
            StrawberryStarletteRouteFactory,
        )

        context.register_impl(RouteFactoryABC, StrawberryStarletteRouteFactory)

    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_aws(context: InjectyContext):
    try:
        from servey.servey_aws.authorizer.kms_authorizer_factory import (
            KmsAuthorizerFactory,
        )
        from servey.security.authorizer.authorizer_factory_abc import (
            AuthorizerFactoryABC,
        )

        context.register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory)

        from servey.servey_aws.event_handler.event_handler_abc import (
            EventHandlerFactoryABC,
        )
        from servey.servey_aws.event_handler.event_handler import EventHandlerFactory
        from servey.servey_aws.event_handler.api_gateway_event_handler import (
            ApiGatewayEventHandlerFactory,
        )
        from servey.servey_aws.event_handler.appsync_event_handler import (
            AppsyncEventHandlerFactory,
        )
        from servey.servey_aws.event_handler.sqs_event_handler import (
            SqsEventHandlerFactory,
        )

        context.register_impls(
            EventHandlerFactoryABC,
            [
                EventHandlerFactory,
                AppsyncEventHandlerFactory,
                ApiGatewayEventHandlerFactory,
                SqsEventHandlerFactory,
            ],
        )

        from servey.servey_aws.aws_websocket_sender import (
            AWSWebsocketSenderFactory,
        )

        context.register_impl(WebsocketSenderFactoryABC, AWSWebsocketSenderFactory)

        from servey.servey_aws.sqs_background_invoker import (
            SqsBackgroundInvokerFactory,
        )

        context.register_impl(BackgroundInvokerFactoryABC, SqsBackgroundInvokerFactory)

        from servey.servey_aws.router.router_abc import RouterABC
        from servey.servey_aws.router.api_gateway_router import APIGatewayRouter
        from servey.servey_aws.router.appsync_router import AppsyncRouter
        from servey.servey_aws.router.router import Router

        context.register_impls(RouterABC, [APIGatewayRouter, AppsyncRouter, Router])

    except ModuleNotFoundError as e:
        raise_non_ignored(e)


# noinspection DuplicatedCode
def configure_serverless(context: InjectyContext):
    try:
        from servey.servey_aws.serverless.yml_config.yml_config_abc import YmlConfigABC
        from servey.servey_aws.serverless.yml_config.action_function_config import (
            ActionFunctionConfig,
        )

        # pylint: disable=E0001
        from servey.servey_aws.serverless.yml_config.appsync_config import AppsyncConfig
        from servey.servey_aws.serverless.yml_config.kms_key_config import KmsKeyConfig
        from servey.servey_aws.serverless.yml_config.event_channel_function_config import (
            EventChannelFunctionConfig,
        )

        context.register_impls(
            YmlConfigABC,
            [
                ActionFunctionConfig,
                AppsyncConfig,
                KmsKeyConfig,
                EventChannelFunctionConfig,
            ],
        )

        from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
            TriggerHandlerABC,
        )
        from servey.servey_aws.serverless.trigger_handler.web_trigger_handler import (
            WebTriggerHandler,
        )
        from servey.servey_aws.serverless.trigger_handler.fixed_rate_trigger_handler import (
            FixedRateTriggerHandler,
        )

        context.register_impls(
            TriggerHandlerABC, [WebTriggerHandler, FixedRateTriggerHandler]
        )

        from servey.servey_aws.serverless.yml_config.cloudfront_config import (
            CloudfrontConfig,
        )
        from servey.servey_aws.serverless.yml_config.static_site_bucket_config import (
            StaticSiteBucketConfig,
        )

        context.register_impls(YmlConfigABC, [CloudfrontConfig, StaticSiteBucketConfig])

    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_celery(context: InjectyContext):
    try:
        from servey.servey_celery.celery_background_invoker import (
            CeleryBackgroundInvokerFactory,
        )

        context.register_impl(
            BackgroundInvokerFactoryABC, CeleryBackgroundInvokerFactory
        )

        from servey.servey_celery.celery_config.celery_config_abc import CeleryConfigABC
        from servey.servey_celery.celery_config.fixed_rate_trigger_config import (
            FixedRateTriggerConfig,
        )
        from servey.servey_celery.celery_config.background_invoker_config import (
            BackgroundInvokerConfig,
        )
        from servey.servey_celery.celery_config.websocket_config import WebsocketConfig

        context.register_impls(
            CeleryConfigABC,
            [FixedRateTriggerConfig, BackgroundInvokerConfig, WebsocketConfig],
        )

    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_jinja2(context: InjectyContext):
    try:
        # We import Template to test that jinja2 is actually present
        # pylint: disable=W0611
        from jinja2 import Template

        configure_web_page_action_endpoint_factory(context)
        configure_web_page_event_handler(context)
        configure_web_page_trigger_handler(context)
    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_web_page_action_endpoint_factory(context: InjectyContext):
    try:
        from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
            ActionEndpointFactoryABC,
        )
        from servey.servey_web_page.web_page_action_endpoint_factory import (
            WebPageActionEndpointFactory,
        )

        context.register_impl(ActionEndpointFactoryABC, WebPageActionEndpointFactory)
    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_web_page_event_handler(context: InjectyContext):
    try:
        from servey.servey_aws.event_handler.event_handler_abc import (
            EventHandlerFactoryABC,
        )
        from servey.servey_web_page.web_page_event_handler import (
            WebPageEventHandlerFactory,
        )

        context.register_impl(EventHandlerFactoryABC, WebPageEventHandlerFactory)
    except ModuleNotFoundError as e:
        raise_non_ignored(e)


def configure_web_page_trigger_handler(context: InjectyContext):
    try:
        from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
            TriggerHandlerABC,
        )
        from servey.servey_web_page.web_page_trigger_handler import (
            WebPageTriggerHandler,
        )

        context.register_impl(TriggerHandlerABC, WebPageTriggerHandler)
    except ModuleNotFoundError as e:
        raise_non_ignored(e)


# Due to the use of extras, certain modules may not be present, but that's okay
_NO_MODULE_NAMED = "No module named '"
_IGNORABLE_MISSING_MODULE_NAMES = {
    "celery",
    "requests",
    "jinja2",
    "ruamel",
    "ruamel.yaml",
    "boto3",
    "starlette",
    "strawberry",
}


def raise_non_ignored(e: ModuleNotFoundError):
    msg = str(e)
    if msg.startswith(_NO_MODULE_NAMED):
        module_name = msg[len(_NO_MODULE_NAMED) : -1]
        if module_name in _IGNORABLE_MISSING_MODULE_NAMES:
            LOGGER.debug(msg)
            return
    raise e
