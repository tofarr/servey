"""
Module for running a local python debugging server based on Uvicorn, along with a
local_schedule_mount for actions.
"""
import argparse
import json
import logging
import os

from servey.errors import ServeyError

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)
DEBUG = int(os.environ.get("SERVER_DEBUG", "1")) == 1
HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "8000"))
CELERY_BROKER = os.environ.get("CELERY_BROKER")


def start_http_server():
    import uvicorn

    app = "servey.servey_starlette.starlette_app:app"
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level=LOGLEVEL.lower(),
        reload=DEBUG,
        reload_includes=["*.j2", "*.py"],
        reload_dirs=["."],
    )


def start_scheduler():
    if CELERY_BROKER:
        # noinspection PyUnresolvedReferences
        import servey.servey_celery.celery_app
    else:
        os.environ["SERVEY_DAEMON"] = "1"
        # noinspection PyUnresolvedReferences
        import servey.servey_thread.__main__


def generate_openapi_schema():
    if "SERVEY_STRICT_SCHEMA" not in os.environ:
        os.environ["SERVEY_STRICT_SCHEMA"] = "1"
    from servey.servey_starlette.route_factory.openapi_route_factory import (
        OpenapiRouteFactory,
    )

    factory = OpenapiRouteFactory()
    schema = factory.openapi_schema()
    output_file = os.environ.get("OUTPUT_FILE", "openapi.json")
    json.dump(schema, output_file)


def generate_graphql_schema():
    from servey.servey_aws.serverless.yml_config.appsync_config import AppsyncConfig

    config = AppsyncConfig()
    config.build_appsync_schema()


def main():
    parser = argparse.ArgumentParser(description="Servey")
    parser.add_argument("--run", default="server")
    args, _ = parser.parse_known_args()
    if args.run == "sls":
        # noinspection PyUnresolvedReferences
        import servey.servey_aws.serverless.__main__
    elif args.run == "openapi":
        generate_openapi_schema()
    elif args.run == "graphql-schema":
        generate_graphql_schema()
    elif args.run == "action":
        # noinspection PyUnresolvedReferences
        import servey.servey_direct.__main__
    elif args.run == "server":
        start_scheduler()
        start_http_server()
    else:
        raise ServeyError(f"unknown:{args.run}")


if __name__ == "__main__":
    main()
