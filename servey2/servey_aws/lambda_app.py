"""
Global lambda app namespace, using reflection.

I suppose we could use code generation and be more specific here, and use code generation to deliberately
enumerate the lambda handlers (And control the imports in the lambda env), though I am currently not fully
clear on what the benefits / drawbacks to this approach.
"""
from servey2.servey_aws.lambda_handler_factory import create_lambda_handlers

for h in create_lambda_handlers():
    globals()[h.action_meta.name] = h
