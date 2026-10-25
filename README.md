# AWS Serverless Data Pipeline with Python: S3, Lambda & DynamoDB

A hands-on AWS project built with **Python** and **boto3**. It covers three common cloud tasks:

1. **Uploading files to Amazon S3** automatically from a local folder
2. **Running serverless code on AWS Lambda** that calls an external REST API and logs results to CloudWatch
3. **Storing API data in Amazon DynamoDB** from a Lambda function, with IAM permissions and environment-based configuration

I built this while moving into Cloud/DevOps engineering, to practice working with AWS the way real teams do: from code and the command line, not only the console.

---

## Architecture

```
                         ┌──────────────────────────┐
  Local machine          │        Amazon S3          │
  my-assets/  ──boto3──▶ │  (bucket: uploaded files) │
                         └──────────────────────────┘

  ┌──────────────────────┐     HTTPS      ┌────────────────────────────┐
  │ JSONPlaceholder API  │ ◀───────────── │       AWS Lambda           │
  │ /users (public JSON) │ ─────────────▶ │  (Python, lambda_handler)  │
  └──────────────────────┘                └─────────────┬──────────────┘
                                                        │ boto3 put_item
                                        logs            ▼
                              ┌─────────────────┐  ┌──────────────────────────┐
                              │ CloudWatch Logs │  │ DynamoDB table           │
                              └─────────────────┘  │ jsonplaceholder-users    │
                                                   │ partition key: id (Num)  │
                                                   └──────────────────────────┘
```

---

## What each part does

### 1. `upload_to_s3.py`: bulk upload to S3

Runs on my machine. It loops over every file in the `my-assets/` folder and uploads it to an S3 bucket with `boto3.client("s3").upload_file()`.

```
Uploaded: my-image.png
Uploaded: hello.txt
All files uploaded successfully!
```

### 2. `lambda_function.py`: Lambda calling an external API

A Lambda function that fetches 10 users from the public [JSONPlaceholder](https://jsonplaceholder.typicode.com/users) API, prints each name to **CloudWatch Logs**, and returns a JSON response with the total count and the list of names. It uses only the Python standard library (`urllib`), so no extra packages are needed. Errors are logged and re-raised so Lambda marks the run as failed.

### 3. `lambda_function_dynamodb.py`: Lambda writing to DynamoDB

Extends the first function: it fetches the same users and **saves each full record (including nested address and company) into a DynamoDB table** with `table.put_item()`.

- Table name comes from the environment variable **`TABLE_NAME`** (not hardcoded)
- Table partition key: **`id` (Number)**, which matches the API's numeric user ID
- The Lambda execution role only needs **`dynamodb:PutItem`** on this table (least-privilege IAM)
- Validates the API response before writing, and re-raises errors so failures show up in CloudWatch metrics

`lambda_users_demo.zip` is the packaged Lambda code used for deployment.

---

## Skills demonstrated

| Area            | What I used                                                                        |
| --------------- | ---------------------------------------------------------------------------------- |
| Programming     | Python 3, boto3, REST API calls with `urllib`, JSON handling, error handling       |
| AWS services    | S3, Lambda, DynamoDB, IAM, CloudWatch Logs                                         |
| Cloud practices | Environment variables for config, least-privilege IAM policies, no secrets in code |
| Tooling         | AWS CLI v2 (`aws login`), virtual environments, Git & GitHub, VS Code              |

---

## Project structure

```
s3-boto3-lambda-dynamodb/
├── my-assets/                   # Sample files uploaded to S3
│   ├── hello.txt
│   └── my-image.png
├── upload_to_s3.py              # Local script: upload folder contents to S3
├── lambda_function.py           # Lambda: fetch users from API, log to CloudWatch
├── lambda_function_dynamodb.py  # Lambda: fetch users from API, save to DynamoDB
├── lambda_users_demo.zip        # Lambda deployment package
├── requirements.txt
└── .gitignore
```

---

## How to run it

### Prerequisites

- AWS account
- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Python 3.10+

### Part 1: Upload files to S3 (local)

```bash
# Sign in to AWS from the terminal
aws login
aws sts get-caller-identity

# Set up Python
git clone https://github.com/hossenra/s3-boto3-lambda-dynamodb.git
cd s3-boto3-lambda-dynamodb
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create a bucket (name must be globally unique), set it as bucket_name in upload_to_s3.py
aws s3 mb s3://your-unique-bucket-name
python upload_to_s3.py
aws s3 ls s3://your-unique-bucket-name/
```

### Part 2: Lambda that calls the API

1. Lambda console → **Create function** → Python runtime
2. Paste the code from `lambda_function.py` (or upload `lambda_users_demo.zip`)
3. Click **Test** and check the user names in **CloudWatch Logs**

### Part 3: Lambda that saves to DynamoDB

1. DynamoDB → **Create table**
   - Name: `jsonplaceholder-users`
   - Partition key: `id`, type **Number**
2. Create a Lambda function with the code from `lambda_function_dynamodb.py`
   (handler: `lambda_function_dynamodb.lambda_handler`, or rename the file to `lambda_function.py`)
3. **Configuration → Environment variables**: `TABLE_NAME = jsonplaceholder-users`
4. **Configuration → Permissions**: add a policy to the execution role allowing `dynamodb:PutItem` on the table ARN
5. Increase the timeout to ~15 seconds (default 3s can be too short for the API call plus 10 writes)
6. Run **Test**, then open the table → **Explore items** to see the 10 users

---

## Security notes

- No AWS access keys in this repository. Locally, credentials come from `aws login` (temporary); in Lambda, from the function's IAM role.
- The DynamoDB Lambda gets only the one permission it needs (`PutItem`).
- `.venv/` and installers are excluded via `.gitignore`.

---

## What I learned

- How boto3 finds credentials, and debugging real errors: `NoCredentials`, `NoSuchBucket`, `MissingDependencyException` (needed `botocore[crt]` for `aws login` credentials)
- How Lambda gets permissions through its execution role instead of keys
- Why configuration belongs in environment variables, not in code
- How DynamoDB partition keys must match the data type being written
- Using CloudWatch Logs to see what a Lambda function actually did

---

## Next steps

- [ ] Trigger a Lambda automatically when a file lands in S3 (S3 event notification)
- [ ] Expose the users through API Gateway as a REST endpoint
- [ ] Define the bucket, table, Lambda and IAM role with Terraform
- [ ] Deploy the Lambda automatically with GitHub Actions

---

## Author

**Razibul Hossen**, Cloud & DevOps learner based in Germany
GitHub: [@hossenra](https://github.com/hossenra)
