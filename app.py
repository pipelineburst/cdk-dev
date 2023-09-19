#!/usr/bin/env python3

import aws_cdk as cdk
from cdk_dev.sbom_chart_stack import WorkloadDeploy
from cdk_dev.sbom_ecr_stack import EcrInspectorStack
from cdk_dev.sbom_eks_stack import EksSbomStack


app = cdk.App()

stack1 = EcrInspectorStack(app, "EcrInspectorStack", 
            description="Provision resources for ECR and SBOM exports", 
            termination_protection=False, 
            tags={"dep":"digital"}, 
            env=cdk.Environment(region="eu-west-1")
        )

stack2 = EksSbomStack(app, "EksSbomStack", 
            description="Provision EKS cluster for image signature and SBOM validation", 
            termination_protection=False, 
            tags={"dep":"digital"}, 
            env=cdk.Environment(region="eu-west-1")
        )

stack3 = WorkloadDeploy(app, "WorkloadDeployStack",
            description="Deploy workloads into EKS cluster for image and SBOM validation", 
            termination_protection=False, 
            tags={"dep":"digital"}, 
            env=cdk.Environment(region="eu-west-1"),
            cluster=stack2.ekscluster,
        )    

# stack3.add_dependency(stack2)

cdk.Tags.of(stack1).add(key="owner",value="Digital")
cdk.Tags.of(stack2).add(key="owner",value="Digital")

app.synth()
