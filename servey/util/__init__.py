import base64
import hashlib
import json
import os
import re

from marshy.types import ExternalType

_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(name: str) -> str:
    return _PATTERN.sub("_", name).lower()


def secure_hash(item: ExternalType) -> str:
    item_json = json.dumps(item)
    item_bytes = item_json.encode("utf-8")
    return secure_hash_content(item_bytes)


def secure_hash_content(content: bytes) -> str:
    sha = hashlib.sha256()
    sha.update(content)
    hash_bytes = sha.digest()
    b64_bytes = base64.b64encode(hash_bytes)
    b64_str = b64_bytes.decode("utf-8")
    return b64_str


def get_servey_main():
    servey_main = os.environ.get("SERVEY_MAIN")
    if servey_main:
        servey_main = to_snake_case(servey_main)
    else:
        servey_main = "servey_main"
    return servey_main
