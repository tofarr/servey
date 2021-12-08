from servey.authorizer.authorizer_abc import AuthorizerABC


class NoAuthorizer(AuthorizerABC):

    def authorize(self, token: str):
        """ No servey required"""
