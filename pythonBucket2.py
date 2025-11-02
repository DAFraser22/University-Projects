import boto3
from botocore.exceptions import NoCredentialsError

# AWS credentials
AWS_ACCESS_KEY = "Access Key"
AWS_SECRET_KEY = "Secret Key"
AWS_SESSION_TOKEN = "Session Token"

# S3 bucket and file configuration
BUCKET_NAME = "dht11pibucketdylan"
FILE_NAME = "sensor_output.txt"  # File to upload (in the same directory as the script)
S3_KEY = "sensor_output.txt"     # Desired name for the file in the S3 bucket

def upload_to_s3():
    try:
        # Create an S3 client using AWS credentials
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            aws_session_token=AWS_SESSION_TOKEN  # Optional, include if using temporary credentials
        )

        # Upload the file to the S3 bucket
        s3.upload_file(FILE_NAME, BUCKET_NAME, S3_KEY)
        print(f"File '{FILE_NAME}' successfully uploaded to bucket '{BUCKET_NAME}' as '{S3_KEY}'.")

    except FileNotFoundError:
        print(f"Error: The file '{FILE_NAME}' was not found in the current directory.")
    except NoCredentialsError:
        print("Error: AWS credentials not available.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    upload_to_s3()

