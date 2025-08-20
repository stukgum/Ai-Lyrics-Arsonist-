import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional

# Initialize S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('S3_ENDPOINT'),
    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
    region_name='us-east-1'
)

BUCKET_NAME = os.getenv('S3_BUCKET', 'beatlyrics')

def upload_file_to_s3(file_data: bytes, key: str, content_type: str) -> str:
    """Upload file to S3 and return URL"""
    
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=file_data,
            ContentType=content_type
        )
        
        # Generate URL
        url = f"{os.getenv('S3_ENDPOINT')}/{BUCKET_NAME}/{key}"
        return url
        
    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {str(e)}")

def download_from_s3(key: str) -> bytes:
    """Download file from S3"""
    
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        return response['Body'].read()
        
    except ClientError as e:
        raise RuntimeError(f"S3 download failed: {str(e)}")

def delete_from_s3(key: str) -> bool:
    """Delete file from S3"""
    
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        return True
        
    except ClientError as e:
        print(f"S3 delete failed: {str(e)}")
        return False
