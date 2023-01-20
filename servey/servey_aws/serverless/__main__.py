import argparse
import os
from typing import Set

from servey.util import get_servey_main


def generate_serverless_scaffold(skip_configs: Set[str]):
    main_serverless_yml_file = (
        os.environ.get("MAIN_SERVERLESS_YML_FILE") or "serverless.yml"
    )
    if not os.path.exists(main_serverless_yml_file):
        from servey.servey_aws.serverless import yml_config
        from importlib import resources

        template = resources.read_text(yml_config, "serverless_template.yml")
        serverless_yml_content = template.format(
            serverless_service_name=get_servey_main().title().replace("_", ""),
            service_name=get_servey_main(),
        )
        with open(main_serverless_yml_file, "w") as f:
            f.write(serverless_yml_content)
    from servey.servey_aws.serverless.yml_config.yml_config_abc import configure

    configure(main_serverless_yml_file, skip_configs)


parser = argparse.ArgumentParser(description="Servey")
parser.add_argument("--run", default="sls")
parser.add_argument("--skip-configs", nargs="+", default=[])
args = parser.parse_args()
generate_serverless_scaffold(set(args.skip_configs))
