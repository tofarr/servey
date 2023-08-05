import os
from typing import List

CORS_ALLOWED_ORIGINS = "CORS_ALLOWED_ORIGINS"


def get_allowed_origins() -> List[str]:
    allowed_origins = os.environ.get(CORS_ALLOWED_ORIGINS) or ""
    result = (a.strip() for a in allowed_origins.split(","))
    result = [a for a in result if a]
    return result
