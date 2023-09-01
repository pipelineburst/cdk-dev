#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_dev.cdk_dev_stack import CdkDevStack


app = cdk.App()
CdkDevStack(app, "cdk-dev")

app.synth()
