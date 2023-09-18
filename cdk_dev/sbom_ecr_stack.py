"""Provision Amazon ECR enhanced scanning with Amazon Inspector"""
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms as kms,
    aws_ecr as ecr,
    custom_resources as cr,
    RemovalPolicy,
)

class EcrInspectorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ### Update ECR private registry level properties
        # 1. Define the input dictionary content for the putRegistryScanningConfiguration AwsSdk call
        
        onUpdateRegistryParams = {
            "scanType": 'ENHANCED',
            "rules": [
                {
                    'scanFrequency': 'CONTINUOUS_SCAN',
                    'repositoryFilters': [
                        {
                            'filter': 'string',
                            'filterType': 'WILDCARD'
                        },
                    ]
                },
            ]
        }

        # 2. Define a custom resource to make an putRegistryScanningConfiguration AwsSdk call to the Amazon ECR API     
           
        registry_cr = cr.AwsCustomResource(self, "EnhancedScanningEnabler",
                on_create=cr.AwsSdkCall(
                    service="ECR",
                    action="putRegistryScanningConfiguration",
                    parameters=onUpdateRegistryParams,
                    physical_resource_id=cr.PhysicalResourceId.of("Parameter.ARN")),
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
                    )
            )
 
        # 3. Define a IAM permission policy for the custom resource    
              
        registry_cr.grant_principal.add_to_principal_policy(iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["inspector2:ListAccountPermissions", "inspector2:Enable", "iam:CreateServiceLinkedRole"],
                resources=["*"],
                )
        )
        
        # ### Provision a ECR private repository
        # # Create the ECR container image repository with the ECR construct
        
        # repository = ecr.Repository(self, "my-ecr-image-repository",
        #     repository_name="my-ecr-image-repository",
        #     image_scan_on_push=True,
        #     image_tag_mutability=ecr.TagMutability.IMMUTABLE,
        #     encryption=ecr.RepositoryEncryption.KMS,
        # )
        
        # # Apply a life cycle rule to the repository we just created
        
        # repository_lcr = repository.add_lifecycle_rule(
        #     max_image_age=Duration.days(30)
        #     )

        ### Create KMS asymmetric signing key with an alias
        
        key = kms.Key(self, "MyKey",
            key_spec=kms.KeySpec.RSA_4096,
            key_usage=kms.KeyUsage.SIGN_VERIFY,
            alias="signingkey"
        )
        
        add_key_policy = key.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["kms:*"],
                resources=["*"],
                principals=[iam.ServicePrincipal("inspector2.amazonaws.com")],
                conditions={
                    "ArnLike": {
                            "aws:SourceArn": "arn:aws:inspector2:"
                            + "eu-west-1"
                            + ":"
                            + "736915441651"
                            + ":report/*"
                        },
                    "StringEquals": {
                            "aws:SourceAccount": "736915441651"
                        }
                    },
                )
        )
        
        ### Create Sbom S3 bucket
        bucket = s3.Bucket(self, "SbomValidationBucket",
            bucket_name="validation-sbom-bucket-u4jedu2",
            auto_delete_objects=True,
            versioned=True,
            bucket_key_enabled=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            encryption=s3.BucketEncryption.KMS,
            intelligent_tiering_configurations=[
                s3.IntelligentTieringConfiguration(
                name="my_s3_tiering",
                archive_access_tier_time=Duration.days(90),
                deep_archive_access_tier_time=Duration.days(180),
                prefix="prefix",
                tags=[s3.Tag(
                    key="key",
                    value="value"
                )]
             )],      
            lifecycle_rules=[
                s3.LifecycleRule(
                    noncurrent_version_expiration=Duration.days(7)
                )
            ],
        )

        # Create S3 bucket policy for inspector sbom export permissions
        add_s3_policy = bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject","s3:PutObject","s3:AbortMultipartUpload"],
                resources=[bucket.arn_for_objects("*")],
                principals=[iam.ServicePrincipal("inspector2.amazonaws.com")],
                conditions={
                    "ArnLike": {
                            "aws:SourceArn": "arn:aws:inspector2:"
                            + "eu-west-1"
                            + ":"
                            + "736915441651"
                            + ":report/*"
                        },
                    "StringEquals": {
                            "aws:SourceAccount": "736915441651"
                        }
                    },
                )
            )
