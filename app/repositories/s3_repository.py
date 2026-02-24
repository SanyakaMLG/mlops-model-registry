import boto3
from fastapi import HTTPException
from app.core.config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, BUCKET_NAME, S3_PUBLIC_ENDPOINT

class S3Repository:
    def __init__(self):
        self.client = boto3.client(
            's3', endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name='us-east-1'
        )
        self.bucket = BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except:
            self.client.create_bucket(Bucket=self.bucket)

    def upload_file(self, file_obj, s3_key: str) -> str:
        try:
            self.client.upload_fileobj(file_obj, self.bucket, s3_key)
            return f"s3://{self.bucket}/{s3_key}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 Upload failed: {str(e)}")

    def generate_presigned_url(self, s3_uri: str) -> str:
        s3_path = s3_uri.replace(f"s3://{self.bucket}/", "")
        try:
            url = self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket, 'Key': s3_path},
                ExpiresIn=3600
            )
            return url.replace(S3_ENDPOINT, S3_PUBLIC_ENDPOINT)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate URL: {str(e)}")