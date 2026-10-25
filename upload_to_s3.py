
import boto3
from pathlib import Path

# Configuration
bucket_name = "razibul-2026-bucket1" # create an unique bucket in AWS
folder_path = Path("./my-assets")

# Create S3 client (uses configured AWS credentials)
s3 = boto3.client("s3")

# Upload all files in the folder
for file_path in folder_path.iterdir():
    if file_path.is_file():
        s3.upload_file(
            str(file_path),
            bucket_name,
            file_path.name
        )
        print(f"Uploaded: {file_path.name}")

print("All files uploaded successfully!")

