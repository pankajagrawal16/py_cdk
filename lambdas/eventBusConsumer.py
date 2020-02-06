import json
from datetime import datetime

import boto3
import jsonschema
from jsonschema import ValidationError

boto3.setup_default_session(profile_name='usermgt')
cloud_watch = boto3.client('cloudwatch')
schema = boto3.client('schemas')


def main(event, context):
    try:
        validate_event(event)
    except ValidationError as err:
        print(f"Invalid event! Event {event} does not validates with configured schema. \n {err}")
        return {
            'statusCode': 400,
            'body': "Event is invalid for the schema"
        }

    difference, response = _calculate_delay(event)

    _push_metrics(difference)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def validate_event(event):
    response = schema.describe_schema(
        RegistryName='DummySchemaRegistry',
        SchemaName='DummyCheck'
    )

    json_content = json.loads(response['Content'])
    jsonschema.validate(
        instance=event,
        schema=json_content,

    )
    print(f"Valid event! Event {event} validates with configured schema: {response['Content']}")


def _push_metrics(difference):
    cloud_watch_response = cloud_watch.put_metric_data(
        MetricData=[
            {
                'MetricName': 'EventsDelay',
                'Dimensions': [
                    {
                        'Name': 'Version',
                        'Value': '1.0'
                    }
                ],
                'Unit': 'Milliseconds',
                'Value': difference
            },
        ],
        Namespace='POCEventBridge'
    )

    print(f'Cloud watch response: {cloud_watch_response}')


def _calculate_delay(event):
    receive_time = datetime.now()
    start_time = datetime.strptime(event['detail']['Time'], "%Y-%m-%d %H:%M:%S.%f")
    difference = (receive_time - start_time).total_seconds() * 1000
    response = {
        'EventInitiatedTime': start_time.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
        'EventReceivedTIme': receive_time.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
        'DelayTimeInMs': difference
    }
    print(response)
    return difference, response


if __name__ == '__main__':
    eve = {
        'time': "2020-02-04T10:43:46Z"
    }

    main(eve, None)
