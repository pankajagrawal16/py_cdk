import json
import pytest

from aws_cdk import core
from py_cdk.py_cdk_stack import PyCdkStack


def get_template():
    app = core.App()
    PyCdkStack(app, "py-cdk")
    return json.dumps(app.synth().get_stack("py-cdk").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
