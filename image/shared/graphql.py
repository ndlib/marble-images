from urllib import request, error
from socket import timeout
from datetime import datetime
import json
from . import aws_utility
from . import logger
from . import config


graphql_api_key = aws_utility.get_graphql_api_key()
graphql_api_url = aws_utility.get_graphql_api_url()


def _request_headers() -> dict:
    return {"x-api-key": graphql_api_key}


def _request_url() -> dict:
    return graphql_api_url


def _serialization_helper(o):
    if isinstance(o, datetime):
        return o.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def run_operation(query, operation_name, variables={}):
    data = json.dumps({
        "query": query,
        "variables": variables,
        "operationName": operation_name
    },
        default=_serialization_helper,
        # ignore_nan=True
    )
    r = request.Request(
        headers=_request_headers(),
        url=_request_url(),
        method="POST",
        data=data.encode("utf8")
    )
    try:
        response = request.urlopen(r, timeout=config.SOCKET_TIMEOUT).read()
        return json.loads(response.decode("utf8"))
    except error.URLError as ue:
        logger.error(f"Error to {_request_url()} with {variables}: {ue}")
        return {}
    except timeout:
        logger.error(f"Socket timed out to {_request_url()} with params: {data}")
        return {}
