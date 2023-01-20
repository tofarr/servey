import os
from dataclasses import dataclass


@dataclass
class IndexModel:
    is_server_debug: bool = os.environ.get("SERVER_DEBUG") == "1"
