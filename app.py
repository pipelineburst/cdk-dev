#!/usr/bin/env python3

import aws_cdk as cdk
from cdk_dev.ecr_stack import EcrStack
from cdk_dev.vpc_stack import VpcStack
from cdk_dev.eks_stack import EksStack
from cdk_dev.chart_stack import WorkloadDeploy

app = cdk.App()

stack1 = VpcStack(app, "VpcStack",
            description="Provision custom VPC resources", 
            termination_protection=False, 
            tags={"project":"imagevalidation"}, 
            env=cdk.Environment(region="eu-west-1"),
        )

stack2 = EksStack(app, "EksStack", 
            description="Provision EKS cluster resources", 
            termination_protection=False, 
            tags={"project":"imagevalidation"}, 
            env=cdk.Environment(region="eu-west-1"),
            vpc=stack1.eksvpc,
        )

stack3 = EcrStack(app, "EcrStack", 
            description="Provision ECR resources with enhanced scanning", 
            termination_protection=False, 
            tags={"project":"imagevalidation"}, 
            env=cdk.Environment(region="eu-west-1"),
        )

stack4 = WorkloadDeploy(app, "WorkloadDeployStack",
            description="Deploy workloads and addons into EKS cluster for image verification", 
            termination_protection=False, 
            tags={"project":"imagevalidation"}, 
            env=cdk.Environment(region="eu-west-1"),
            cluster=stack2.ekscluster,
        )

stack2.add_dependency(stack1)
stack3.add_dependency(stack2)
stack4.add_dependency(stack3)

cdk.Tags.of(stack1).add(key="owner",value="validation")
cdk.Tags.of(stack2).add(key="owner",value="validation")
cdk.Tags.of(stack3).add(key="owner",value="validation")

app.synth()
