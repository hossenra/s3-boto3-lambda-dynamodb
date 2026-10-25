"""AWS Lambda classroom demo: fetch users and log their names to CloudWatch."""

import json
import urllib.request

API_URL = "https://jsonplaceholder.typicode.com/users"


def lambda_handler(event, context):
    """Fetch a public JSON API, print the names, and return a summary."""
    print("Starting Lambda: fetching users from JSONPlaceholder...")

    request = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/json", "User-Agent": "lambda-users-demo/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            users = json.load(response)
    except Exception as error:
        print(f"ERROR: Failed to fetch users: {error}")
        raise

    names = [user["name"] for user in users]

    print("User names:")
    for number, name in enumerate(names, start=1):
        print(f"{number}. {name}")

    print(f"Total users: {len(names)}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Success", "total_users": len(names), "names": names}),
    }
