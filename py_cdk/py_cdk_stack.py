from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lam,
    aws_events_targets as target,
    aws_events as event,
    aws_eventschemas as schema,
    core
)
from aws_cdk.aws_iam import ManagedPolicy
from aws_cdk.aws_lambda import Code, Runtime
from aws_cdk.core import Duration
from pathlib import Path


class PyCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        event_bus = event.EventBus(self, id="DummyEventBus", event_bus_name="DummyEventBus")

        generator_role = iam.Role(self,
                                  id="GeneratorEventBusRole",
                                  assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                                  managed_policies=[
                                      ManagedPolicy.from_aws_managed_policy_name('AmazonEventBridgeFullAccess'),
                                      ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
                                  ]
                                  )

        consumer_role = iam.Role(self,
                                 id="ConsumerEventBusRole",
                                 assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                                 managed_policies=[
                                     ManagedPolicy.from_aws_managed_policy_name('AmazonEventBridgeFullAccess'),
                                     ManagedPolicy.from_aws_managed_policy_name('AmazonEventBridgeSchemasReadOnlyAccess'),
                                     ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                                     ManagedPolicy.from_managed_policy_name(self, 'CloudWatchPutMetricsPolicy', 'PutCloudWatchMetric')
                                 ]
                                 )

        layer = lam.LayerVersion(self, id='CommonLayer', code=Code.from_asset('asset/package'))

        generator = lam.Function(self,
                                 id='EventGeneratorForBus',
                                 code=Code.from_asset('lambdas'),
                                 handler='eventBusGenerator.main',
                                 function_name='EventGeneratorForBus',
                                 timeout=Duration.seconds(60),
                                 memory_size=512,
                                 role=generator_role,
                                 runtime=Runtime.PYTHON_3_7)

        consumer = lam.Function(self,
                                id='EventConsumerForBus',
                                code=Code.from_asset('lambdas'),
                                handler='eventBusConsumer.main',
                                function_name='EventConsumerForBus',
                                timeout=Duration.seconds(60),
                                role=consumer_role,
                                layers=[layer],
                                runtime=Runtime.PYTHON_3_7)

        generator_target = target.LambdaFunction(generator)

        consumer_target = target.LambdaFunction(consumer)

        event.Rule(self,
                   id='DummyCheckRule',
                   description='For measuring response time of customer events',
                   enabled=True,
                   event_bus=event_bus,
                   rule_name='DummyCheckRule',
                   targets=[consumer_target],
                   event_pattern=event.EventPattern(detail_type=['check'])
                   )

        event.Rule(self,
                   id='GenerateEventsScheduled',
                   enabled=False,
                   rule_name='GenerateEventsScheduled',
                   targets=[generator_target],
                   schedule=event.Schedule.rate(Duration.minutes(1))
                   )

        schema_registry = schema.CfnRegistry(self,
                                             id='DummySchemaRegistry',
                                             registry_name='DummySchemaRegistry',
                                             description='Maintaining schema for events'
                                             )

        schema.CfnSchema(self,
                         id='DummyCheck',
                         registry_name=schema_registry.registry_name,
                         schema_name='DummyCheck',
                         type='OpenApi3',
                         content=Path('schemas/DummyCheck.json').read_text()
                         )
