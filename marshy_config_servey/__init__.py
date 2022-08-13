from typing import Optional

from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

from servey.access_control.authorization import Authorization, ROOT
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import AuthorizerFactoryABC
from servey.access_control.jwt_authorizer_factory import JwtAuthorizerFactory
from servey.action_finder.action_finder_abc import ActionFinderABC
from servey.action_finder.module_action_finder import ModuleActionFinder
from servey.integration.aws.kms_authorizer_factory import KmsAuthorizerFactory

priority = 100


class StupidAuthorizer(AuthorizerABC):

    def authorize(self, token: str) -> Authorization:
        return ROOT

    def encode(self, authorization: Authorization) -> str:
        return 'ROOT'


class StupidAuthorizerFactory(AuthorizerFactoryABC):

    def create_authorizer(self) -> AuthorizerABC:
        return StupidAuthorizer()


def configure(context: MarshallerContext):
    register_impl(ActionFinderABC, ModuleActionFinder, context)
    register_impl(AuthorizerFactoryABC, KmsAuthorizerFactory, context)
    register_impl(AuthorizerFactoryABC, JwtAuthorizerFactory, context)
    register_impl(AuthorizerFactoryABC, StupidAuthorizerFactory, context)

