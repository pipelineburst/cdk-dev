"""Deploy helm chart and other workloads onto EKS cluster"""
import yaml
from constructs import Construct, Dependable
from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_signer as signer,
    aws_iam as iam,
    custom_resources as cr,
)

class WorkloadDeploy(Stack):

    def __init__(self, scope: Construct, construct_id: str, cluster, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster.add_helm_chart("kyverno",
            chart="kyverno",
            repository="https://kyverno.github.io/kyverno/",
            release="kyverno",
            version="3.0.4",
            values={
                "admissionController.replicas": "3",
                "backgroundController.replicas": "2",
                "cleanupController.replicas": "2",
                "reportsController.replicas": "2",
            },
            create_namespace=True,
             namespace="kyverno",
        )

        # Adding signer
        
        onUpdateSignerProfileParams = {
            "profileName": "container_signer_profile",            
            "platformId": "Notation-OCI-SHA384-ECDSA",
            "signatureValidityPeriod": { 
                "type": "MONTHS",
                "value": 12
            },
            "tags": { 
                "owner" : "signer" 
            }
        }

        # Define a custom resource to make an putRegistryScanningConfiguration AwsSdk call to the Amazon ECR API     
           
        container_signer_cr = cr.AwsCustomResource(self, "EnhancedScanningEnabler",
                on_create=cr.AwsSdkCall(
                    service="Signer",
                    action="PutSigningProfile",
                    parameters=onUpdateSignerProfileParams,
                    physical_resource_id=cr.PhysicalResourceId.of("Parameter.ARN")),
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
                    ),
            )
 
        # Define a IAM permission policy for the custom resource    
              
        container_signer_cr.grant_principal.add_to_principal_policy(iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["signer:TagResource", "ecr:*"],
                resources=["*"],
                )
            )


        ### works, but we cannot set a dependency to the kyverno chart
        # with open('cdk_dev/assets/kyverno-cpol-image-verify.yaml') as f:
        #     cluster.add_manifest('cpol',
        #         list(yaml.safe_load_all(f.read()))[0]
        #     )

        # eks.HelmChart(self, "fluxOciChart",
        #     cluster=cluster,
        #     chart="helm-controller",
        #     repository="oci://public.ecr.aws/l0g8r8j6/fluxcd",
        #     create_namespace=True,
        #     namespace="oci",
        # )

        # cluster.add_helm_chart("flux",
        #     chart="sourceController",
        #     repository="oci://ghcr.io/fluxcd-community/charts/flux2",
        #     release="flux",
        #     # values={
        #     #     "git.url":"git@github.com\:pipelineburst/gitops"
        #     # },
        #     create_namespace=True,
        #     namespace="flux-system",
        # )
        
        # # cluster.add_helm_chart("kyverno-policies",
        #     chart="kyverno-policies",
        #     repository="https://kyverno.github.io/kyverno/",
        #     release="kyverno-policies",
        #     version="3.0.4",
        #     create_namespace=False,
        #     namespace="kyverno",
        # )