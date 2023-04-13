import base64
import hashlib
import json
import os
import re

from marshy.types import ExternalType

_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(name: str) -> str:
    return _PATTERN.sub("_", name).lower()


def entity_to_camel_case(name: str) -> str:
    parts = name.split('_')
    result = []
    for part in parts:
        result.append(part[0].upper())
        result.append(part[1:].lower())
    return ''.join(result)


def attr_camel_case(name: str) -> str:
    parts = name.split('_')
    result = [parts[0].lower()]
    for part in parts[1:]:
        result.append(part[0].upper())
        result.append(part[1:].lower())
    return ''.join(result)


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
