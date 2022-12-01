"""
Module for running a local python debugging server based on Uvicorn, along with a
local_schedule_mount for actions.
"""
import argparse
import logging
import os

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
        reload_dirs=["."],
    )


def start_scheduler():
    if CELERY_BROKER:
        import servey.servey_celery.celery_app
    else:
        import servey.servey_thread.threaded_app


def generate_serverless_scaffold():
    main_serverless_yml_file = (
        os.environ.get("MAIN_SERVERLESS_YML_FILE") or "serverless.yml"
    )
    if not os.path.exists(main_serverless_yml_file):
        from servey.servey_aws.serverless import yml_config
        from importlib import resources

        template = resources.read_text(yml_config, "serverless_template.yml")
        serverless_yml_content = template.format(
            service_name=os.environ.get("SERVICE_NAME") or "serveyApp"
        )
        with open(main_serverless_yml_file, "w") as f:
            f.write(serverless_yml_content)
    from servey.servey_aws.serverless.yml_config.yml_config_abc import configure

    configure(main_serverless_yml_file)


def main():
    parser = argparse.ArgumentParser(description="Servey")
    parser.add_argument("--sls-generate", nargs="?", default=False, const=True)
    args = parser.parse_args()
    if args.sls_generate:
        generate_serverless_scaffold()
    else:
        start_http_server()


if __name__ == "__main__":
    main()
