import os

from servey.servey_aws.serverless.yml_config.yml_config_abc import configure

if __name__ == '__main__':
    main_serverless_yml_file = os.environ.get('MAIN_SERVERLESS_YML_FILE') or 'serverless.yml'
    if not os.path.exists(main_serverless_yml_file):
        from servey.servey_aws.serverless import yml_config
        from importlib import resources
        template = resources.read_text(yml_config, 'serverless_template.yml')
        serverless_yml_content = template.format(service_name=os.environ.get("SERVICE_NAME") or 'servey_app')
        with open(main_serverless_yml_file, 'w') as f:
            f.write(serverless_yml_content)
    configure(main_serverless_yml_file)
