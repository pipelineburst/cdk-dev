"""Provision Amazon EKS cluster for image verification with Kyverno"""
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_kms as kms,
    aws_eks as eks,
    aws_iam as iam,
    RemovalPolicy,
)

class EksSbomStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ### 1. Prep work prior to creating the EKS cluster
        # Defining IAM roles for eks-admin and eks-readonly so we can use them later when creating the EKS cluster

        masters_role = iam.Role(
            self,
            "eks-admin",
            role_name="aws-eks-admin",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal(service="eks.amazonaws.com"),
                iam.AnyPrincipal(),  # wihtout it, SSO users can't assume the role
            ),
        )
        masters_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )
        
        readonly_role = iam.Role(
            self,
            "eks-readonly",
            role_name="aws-eks-readonly",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal(service="eks.amazonaws.com"),
                iam.AnyPrincipal(),  # wihtout it, SSO users can't assume the role
            ),
        )
        readonly_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        # Defining cluster logging options

        k8s_logging_params=[
            eks.ClusterLoggingTypes.API,
            eks.ClusterLoggingTypes.AUTHENTICATOR,
            eks.ClusterLoggingTypes.AUDIT,
            eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
            eks.ClusterLoggingTypes.SCHEDULER,
        ]
 
        # Defining a KMS key for secret encryption
        
        eks_key = kms.Key(
            self,
            "eksSecreteEncryptionKey",
            enable_key_rotation=True,
            alias="eksSecreteEncryptionKey",
            removal_policy=RemovalPolicy.DESTROY,
    )

        ### 2. Create EKS cluster from construct library
        # Creating the EKS cluster
        
        cluster = eks.Cluster(self, "EKS validation cluster",
            cluster_name="sbom-validation-cluster",
            version=eks.KubernetesVersion.V1_27,
            masters_role=masters_role, # this adds the eks-admin role to aws-auth as systems:masters
            default_capacity=0,
            cluster_logging=k8s_logging_params,
            secrets_encryption_key=eks_key,
        )
        
        self.ekscluster=cluster # Reference for a downstream Stack

        # Adding a MNG to the cluster 

        masters_role.grant_assume_role(cluster.admin_role) # grant permission to masters_role to assume he cluster admin_role

        cluster.add_nodegroup_capacity("custom-node-group",
            instance_types=[ec2.InstanceType("m5.large")],
            min_size=1,
            disk_size=100,
            ami_type=eks.NodegroupAmiType.BOTTLEROCKET_X86_64,
        )
        
        # Adding our readonly role to aws-auth
        
        cluster.aws_auth.add_role_mapping(
            readonly_role, groups=["system:authenticated"]
        )