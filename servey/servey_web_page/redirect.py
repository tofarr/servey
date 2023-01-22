from dataclasses import dataclass


@dataclass
class Redirect:
    url: str
    status_code: int = 307
