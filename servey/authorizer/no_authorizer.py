from dataclasses import dataclass

from servey.authorizer.authorizer_abc import AuthorizerABC


@dataclass
class NoAuthorizer(AuthorizerABC):

    def authorize(self, token: str):
        """ No servey required"""
