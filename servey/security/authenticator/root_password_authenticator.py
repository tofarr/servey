import base64
import dataclasses
import logging
import os
from dataclasses import field
from typing import Optional

from servey.security.authenticator.password_authenticator_abc import (
    PasswordAuthenticatorABC,
)
from servey.security.authorization import ROOT, Authorization

LOGGER = logging.getLogger(__name__)


def _default_password():
    password = os.environ.get("SERVEY_DEBUG_AUTHENTICATOR_PASSWORD")
    if not password:
        password = (
            base64.b64encode(os.urandom(12))
            .decode("UTF-8")
            .replace("+", "")
            .replace("/", "")
        )
        LOGGER.warning(f"Using Temporary Password: {password}")
    return password


@dataclasses.dataclass
class RootPasswordAuthenticator(PasswordAuthenticatorABC):
    username: str = field(
        default_factory=lambda: os.environ.get("DEBUG_AUTHENTICATOR_USERNAME") or "root"
    )
    password: str = field(default_factory=_default_password)
    authorization: Authorization = field(default=ROOT)

    def authenticate(self, username: str, password: str) -> Optional[Authorization]:
        if self.username == username and self.password == password:
            return self.authorization
