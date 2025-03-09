#!/bin/bash

# Deploy the CDK stack
cd src/cdk
cdk deploy

# Return to the project root
cd ../.. 