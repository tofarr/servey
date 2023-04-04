# Generated Action Example

Demonstrates generated functions and a router to invoke actions in AWS.

## Run

`pip install -r requirements-dev.txt`

`python -m main`

In a browser, navigate to `http://localhost:8000/`. You should see the index page for your project.

## Deploy to AWS

This assumes you already have NodeJs and npm installed (I used npm version 8.15.0), and that you
already have an AWS accounts set up with suitable permissions, with credentials specified in
`$HOME/.aws/credentials` or in your environment.

### Generate serverless definitions with:

`python -m main --run=sls`

This will generate a serverless.yml for you if you don't already have one, and
create and inject various resources from `/serverless_servey` into it.

### Install serverless / serverless plugins:

```
npm install serverless
npm install serverless-python-requirements
npm install serverless-prune-plugin
npm install serverless-appsync-plugin
```

### Deploy the serverless project:

`sls deploy`

This process typically takes a few minutes. Since this project does not define any Route53 or Cloudfront resources,
your API will only have the standard amazon URLs for access.
