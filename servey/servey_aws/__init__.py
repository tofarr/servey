import os


def is_lambda_env():
    result = "AWS_REGION" in os.environ
    return result
