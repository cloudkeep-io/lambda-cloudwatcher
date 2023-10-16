import json
import os
import requests

WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
REGION = os.environ['AWS_REGION']  # Get the region from the Lambda environment


def lambda_handler(event, context):
    # Extracting details from the CloudWatch Alarm
    alarm_name = event['detail']['alarmName']
    new_state = event['detail']['newState']['value']
    reason = event['detail']['newState']['reason']

    # Constructing the CloudWatch Alarm URL
    alarm_url = (
        f"https://console.aws.amazon.com/cloudwatch/home"
        f"?region={REGION}#alarmsV2:alarm/{alarm_name}"
    )

    # Determine color based on the newState value
    if new_state == "ALARM":
        color = "danger"
    elif new_state == "OK":
        color = "good"
    else:  # for "INSUFFICIENT_DATA" or any other potential state
        color = "warning"

    # Constructing the Slack message using blocks and attachments for color
    slack_message = {
        'attachments': [{
            'color': color,
            'blocks': [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "CloudWatch Alarm State Change"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Alarm Name:*\n{alarm_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*New State:*\n{new_state}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Reason:*\n{reason}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Alarm Console URL:*\n{alarm_url}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Alarm"
                        },
                        "url": alarm_url
                    }
                }
            ]
        }]
    }

    # Sending the message to Slack
    response = requests.post(
        WEBHOOK_URL,
        data=json.dumps(slack_message),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, '
            f'the response is:\n{response.text}'
        )

    return {
        'statusCode': 200,
        'body': json.dumps('Message sent to Slack!')
    }
