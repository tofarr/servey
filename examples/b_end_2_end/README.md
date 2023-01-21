# End to End Example

This example is similar to the Hello World example, but also contains a pre-generated serverless.yml that
has mappings for S3, Cloudfront, and route53 (Commented out). This deploys acollection of static and dynamic resources.

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

This will generate and inject various resources from `/serverless_servey` into your serverless.yml.
Note: You'll probably have to update the `custom.staticBucket` from `end2endserveybucket`, as this is used for a 
bucket name and these need to be globally unique within AWS. Also, if you have a global block on public access
to buckets, this will prevent the example from runnng.

### Install serverless / serverless plugins:

```
npm install serverless
npm install serverless-python-requirements
npm install serverless-prune-plugin
npm install serverless-appsync-plugin
npm install serverless-s3-sync
```

### Deploy the serverless project:

`sls deploy`

This process typically takes a few minutes. Since this project does not define any Route53 resources,
your API will only have the standard amazon URLs for access. There is a route53 example commented out.

You should be able to go to your aws console and see the resulting cloudfront distribution
