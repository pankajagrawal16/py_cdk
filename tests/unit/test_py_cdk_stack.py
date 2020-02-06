import json
import pytest

from aws_cdk import core
from py_cdk.py_cdk_stack import PyCdkStack


def get_template():
    app = core.App()
    PyCdkStack(app, "py-cdk")
    return json.dumps(app.synth().get_stack("py-cdk").template)


def test_schema_created():
    assert("AWS::EventSchemas::Schema" in get_template())


def test_registry_created():
    assert("AWS::EventSchemas::Registry" in get_template())
