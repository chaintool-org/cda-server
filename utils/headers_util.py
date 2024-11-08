import logging

from starlette.requests import Request

logger = logging.getLogger(__name__)


def get_header(request: Request, key):
    value = None
    try:
        if key in request.headers:
            value = request.headers[key]
    except Exception:
        logger.warning(f"request headers ,{key} is none")
    return value
