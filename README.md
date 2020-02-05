# twitter cleaner

## build environment

Create a virtual environment dedicated to zappa and tweepy. This will ensure that
the Zappa deploy is as small as possible because Zappa will zip up every package
that pip has installed.

    python3 -m venv ~/venv
    . ~/venv/bin/activate
    pip install tweepy
    pip install zappa

## write yer code

In this case, the aptly named, `twitter_cleaner.py`.

## initialise zappa

    zappa init

This creates a `zappa_settings.json` file which you'll edit so that, at the very least,
it references the correct Lambda handler in your code.

## prepare aws

### zappa user

I created a user called 'zappa' which I'll give minimal permissions to.
Only enough to do the zappa stuff. This user's AWS access keys will be stored
in a specific CircleCI 'context' and will be exported as environment variables
when CircleCI spins up a docker container to run zappa in.

### lambda policy & role

The policy is going to be attached to the **role** that Lambda will need in order
to run your program. In this case, it needs access to a particular S3 bucket, 
the parameter store, amongst other things. I generally create a policy document
(in json format) and store it locally. I can paste it into the correct field in
the AWS console or I can upload it with the `aws` cli tool.

### write helper scripts

As I am going to be using the AWS Parameter Store for storing secrets which I don't
want to store in plaintext in github and would prefer not to use the AWS console a basic
shell script will be used to store the secrets.

I made sure the zappa user and the lambda role included the following permissions:

    "kms:Decrypt",
    "ssm:GetParameterHistory",
    "ssm:GetParametersByPath",
    "ssm:GetParameters",
    "ssm:GetParameter"

## prepare circleci

> `[This is left as an exercise for the reader.]`

### link with github

### populate contexts

The context is something referenced in the .circleci/config.yml file in the root directory
of the repository. This context will contain key/values pairs which will be exported as
environment variables in the CircleCI docker container. In this case, CircleCI needs
to use the AWS access keys that belong to the `zappa` user.

### create your circleci config

## test your setup

### locally

    zappa deploy production
    zappa invoke production 'twitter_clean.lambda_handler'

Fix what's broken

    zappa update production
    zappa invoke production 'twitter_clean.lambda_handler'

Repeat

### remotely

Create a pull request and merge your development branch into `master`. This should kick of
a CircleCI job which will run a docker instance, checkout your repo, and run `zappa deploy production`
or, if that fails, `zappa update production`

You can follow the deployment job in CircleCI, thereafter you can view the Lambda logs via CloudWatch.
Alternatively, `zappa tail production`.
