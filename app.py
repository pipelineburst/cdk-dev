#!/usr/bin/env python3

import aws_cdk as cdk
from cdk_dev.sbom_stack import SbomValStack


app = cdk.App()

stack1 = SbomValStack(app, "sbom-val-cdk", 
            description="Resources for SBOM validation", 
            termination_protection=False, 
            tags={"dep":"digital"}, 
            env=cdk.Environment(region="eu-west-1")
        )

cdk.Tags.of(stack1).add(key="owner",value="Digital")

app.synth()
