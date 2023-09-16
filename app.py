#!/usr/bin/env python3

import aws_cdk as cdk
from cdk_dev.sbom_stack import EcrInspectorStack


app = cdk.App()

stack1 = EcrInspectorStack(app, "EcrInspectorStack", 
            description="Resources for ECR and SBOM validation", 
            termination_protection=False, 
            tags={"dep":"digital"}, 
            env=cdk.Environment(region="eu-west-1")
        )

cdk.Tags.of(stack1).add(key="owner",value="Digital")

app.synth()
