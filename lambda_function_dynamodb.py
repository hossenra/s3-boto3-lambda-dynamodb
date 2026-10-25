"""AWS Lambda demo: fetch JSONPlaceholder users and save them to DynamoDB.

Required Lambda environment variable: TABLE_NAME=jsonplaceholder-users
Required IAM permission: dynamodb:PutItem on the table ARN.
"""

import json
import os
import urllib.request

import boto3

API_URL = "https://jsonplaceholder.typicode.com/users"
TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    print("Fetching users from JSONPlaceholder API...")

    request = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "lambda-users-demo/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            users = json.load(response)

        if not isinstance(users, list):
            raise ValueError("API response was not a list of users")

        for user in users:
            # Save the complete user record, including nested address and company.
            # The numeric user['id'] matches the table's Number partition key.
            table.put_item(Item=user)
            print(f"Saved user ID={user['id']}: {user['name']}")

        print(f"Successfully saved {len(users)} users to DynamoDB table {TABLE_NAME}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Users saved to DynamoDB",
                "table": TABLE_NAME,
                "saved_count": len(users),
            }),
        }

    except Exception as error:
        # Reraise so Lambda records an execution error in CloudWatch metrics.
        print(f"ERROR: Failed to fetch or save users: {error}")
        raise
