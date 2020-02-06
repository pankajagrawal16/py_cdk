from datetime import datetime

import boto3
import time

client = boto3.client('events')


def main(event, context):
    print(event)
    responses = []
    no_of_events = event.get('NoOfEvents')
    no_of_seconds = event.get('NoOfSeconds')

    if no_of_events is None:
        no_of_events = 1
    if no_of_seconds is None:
        no_of_seconds = 1

    for sleeper in range(no_of_seconds):
        for i in range(no_of_events):
            response = client.put_events(
                Entries=[
                    {
                        'Source': 'custom.lambda',
                        'DetailType': 'check',
                        "Detail": "{ \"Name\": \"EventGeneratorForBus\", \"Time\" : \"" + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\"}",
                        'EventBusName': 'DummyEventBus'
                    },
                ]
            )

            responses.append(response)
            print(response)

        print("Sleeping for sec!")
        time.sleep(1)

    return responses
