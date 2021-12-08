import base64
import hashlib
import json

from marshy.types import ExternalItemType


def filter_none(item: ExternalItemType) -> ExternalItemType:
    return {k: v for k, v in item.items() if v is not None}


def secure_hash(item) -> str:
    item_json = json.dumps(item)
    item_bytes = item_json.encode('utf-8')
    sha = hashlib.sha256()
    sha.update(item_bytes)
    hash_bytes = sha.digest()
    b64_bytes = base64.b64encode(hash_bytes)
    b64_str = b64_bytes.decode('utf-8')
    return b64_str