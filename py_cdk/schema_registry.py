from aws_cdk import (
    aws_eventschemas as schema,
    core
)

from pathlib import Path


class SchemaRegistry(core.Construct):

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)

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
