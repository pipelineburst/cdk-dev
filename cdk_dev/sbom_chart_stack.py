"""Deploy helm chart and other workloads onto EKS cluster"""
from constructs import Construct
from aws_cdk import (
    Stack,
)

class WorkloadDeploy(Stack):

    def __init__(self, scope: Construct, construct_id: str, cluster, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster.add_helm_chart("flux",
            chart="flux",
            repository="https://charts.fluxcd.io",
            release="flux",
            values={
                "git.url":"git@github.com\:pipelineburst/gitops"
            },
            create_namespace=True,
            namespace="flux-system",
        )

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

        # cluster.add_helm_chart("kyverno-policies",
        #     chart="kyverno-policies",
        #     repository="https://kyverno.github.io/kyverno/",
        #     release="kyverno-policies",
        #     version="3.0.4",
        #     create_namespace=False,
        #     namespace="kyverno",
        # )