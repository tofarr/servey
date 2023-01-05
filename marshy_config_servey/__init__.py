import logging

from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

from servey.finder.module_subscription_finder import ModuleSubscriptionFinder
from servey.finder.subscription_finder_abc import SubscriptionFinderABC
from servey.subscription.subscription_service import SubscriptionServiceFactoryABC
from servey.util.to_second_datetime_marshaller import (
    ToSecondDatetimeMarshaller,
)

priority = 90
LOGGER = logging.getLogger(__name__)


def configure(context: MarshallerContext):
    from marshy.factory.dataclass_marshaller_factory import DataclassMarshallerFactory

    context.register_factory(
        DataclassMarshallerFactory(priority=101, exclude_dumped_values=tuple())
    )
    context.register_marshaller(ToSecondDatetimeMarshaller())
    configure_finders(context)
    configure_asyncio_subscriptions(context)
    configure_auth(context)
    configure_starlette(context)
    configure_aws(context)
    configure_serverless(context)
    configure_strawberry(context)
    configure_strawberry_starlette(context)
    configure_celery(context)


def configure_finders(context: MarshallerContext):
    from servey.finder.action_finder_abc import ActionFinderABC
    from servey.finder.module_action_finder import ModuleActionFinder

    register_impl(ActionFinderABC, ModuleActionFinder, context)
    register_impl(SubscriptionFinderABC, ModuleSubscriptionFinder, context)


def configure_asyncio_subscriptions(context: MarshallerContext):
    from servey.servey_thread.asyncio_subscription_service import (
        AsyncioSubscriptionServiceFactory,
    )

    register_impl(
        SubscriptionServiceFactoryABC, AsyncioSubscriptionServiceFactory, context
    )


def configure_auth(context: MarshallerContext):
    from servey.security.authorizer.authorizer_factory_abc import AuthorizerFactoryABC
    from servey.security.authorizer.jwt_authorizer_factory import JwtAuthorizerFactory

    register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory, context)


def configure_starlette(context: MarshallerContext):
    try:
        configure_starlette_action_endpoint_factory(context)
        configure_starlette_route_factory(context)
    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("Starlette not installed - Skipping")


def configure_starlette_action_endpoint_factory(context: MarshallerContext):
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

    register_impl(ActionEndpointFactoryABC, ActionEndpointFactory, context)
    register_impl(ActionEndpointFactoryABC, AuthorizingActionEndpointFactory, context)
    register_impl(ActionEndpointFactoryABC, CachingActionEndpointFactory, context)
    register_impl(ActionEndpointFactoryABC, SelfActionEndpointFactory, context)


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
    from servey.servey_starlette.route_factory.subscription_route_factory import (
        SubscriptionRouteFactory,
    )
    from servey.servey_starlette.route_factory.asyncapi_route_factory import (
        AsyncapiRouteFactory,
    )

    register_impl(RouteFactoryABC, ActionRouteFactory, context)
    register_impl(RouteFactoryABC, AuthenticatorRouteFactory, context)
    register_impl(RouteFactoryABC, OpenapiRouteFactory, context)
    register_impl(RouteFactoryABC, SubscriptionRouteFactory, context)
    register_impl(SubscriptionServiceFactoryABC, SubscriptionRouteFactory, context)
    register_impl(RouteFactoryABC, AsyncapiRouteFactory, context)


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

        register_impl(EventHandlerFactoryABC, EventHandlerFactory, context)
        register_impl(EventHandlerFactoryABC, AppsyncEventHandlerFactory, context)
        register_impl(EventHandlerFactoryABC, ApiGatewayEventHandlerFactory, context)
        register_impl(EventHandlerFactoryABC, SqsEventHandlerFactory, context)

        from servey.servey_aws.websocket_subscription_service import (
            AWSWebsocketSubscriptionServiceFactory,
        )

        register_impl(
            SubscriptionServiceFactoryABC,
            AWSWebsocketSubscriptionServiceFactory,
            context,
        )

        from servey.servey_aws.sqs_subscription_service import (
            SqsSubscriptionServiceFactory,
        )

        register_impl(
            SubscriptionServiceFactoryABC,
            SqsSubscriptionServiceFactory,
            context,
        )

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
        from servey.servey_aws.serverless.yml_config.subscription_function_config import (
            SubscriptionFunctionConfig,
        )

        register_impl(YmlConfigABC, ActionFunctionConfig, context)
        register_impl(YmlConfigABC, AppsyncConfig, context)
        register_impl(YmlConfigABC, KmsKeyConfig, context)
        register_impl(YmlConfigABC, SubscriptionFunctionConfig, context)

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


def configure_celery(context: MarshallerContext):
    try:
        from servey.servey_celery.celery_subscription_service import (
            CelerySubscriptionServiceFactory,
        )

        register_impl(
            SubscriptionServiceFactoryABC, CelerySubscriptionServiceFactory, context
        )
    except ModuleNotFoundError as e:
        LOGGER.error(e)
        LOGGER.info("Serverless module not found: skipping")
