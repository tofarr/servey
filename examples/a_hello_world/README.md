# Hello World Example

Deploys a single action with "Hello World"

## Run

`npm install -r requirements.txt`
`python -m main`

In a browser, navigate to `http://localhost:8000/graphiql`

## Deploy to AWS

This assumes you already have nodejs and npm installed (I used npm version 8.15.0), and that you
already have an AWS accounts set up with suitable permissions, with credentials specified in
`$HOME/.aws/credentials` or in your environment.

Generate serverless definitions with:

`python -m main --run=sls`

This will generate a serverless.yml for you if you don't already have one, and
create and inject various resources from `/serverless_servey` into it.

Install serverless packages:

```
npm install serverless
npm install serverless-python-requirements
npm install serverless-prune-plugin
npm install serverless-appsync-plugin
```

Deploy:

`sls deploy`

This will deploy to AWS.
