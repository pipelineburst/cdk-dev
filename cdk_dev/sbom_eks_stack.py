"""Provision Amazon EKS cluster for image verification with Kyverno"""
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms as kms,
    aws_eks as eks,
    custom_resources as cr,
    RemovalPolicy,
)

class EksValStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ### Create EKS cluster from construct library
        
        cluster = eks.Cluster(self, "EKS validation cluster",
            cluster_name="validation-cluster",
            version=eks.KubernetesVersion.V1_27,
            default_capacity=0
        )

        cluster.add_nodegroup_capacity("custom-node-group",
            instance_types=[ec2.InstanceType("m5.large")],
            min_size=4,
            disk_size=100,
            ami_type=eks.NodegroupAmiType.AL2_X86_64_GPU
        )