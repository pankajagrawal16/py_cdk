#!/usr/bin/env python3

from aws_cdk import core

from py_cdk.py_cdk_stack import PyCdkStack


app = core.App()
PyCdkStack(app, "py-cdk", env={'region': 'us-west-2'})

app.synth()
