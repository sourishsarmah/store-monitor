from io import StringIO

import boto3
import pandas as pd

from app.core.config import settings


class CSVUploader:
    def __init__(self, key) -> None:
        self.s3_client = boto3.client("s3")
        self.key = f"{key}.csv"
        self.bucket = settings.S3_BUCKET
        self._part_number = 1
        self._parts = []

        self.__create_bucket(self.bucket)

    def __create_bucket(self, bucket):
        response = self.s3_client.create_bucket(Bucket=bucket)
        return response

    def upload(self, data):
        df = pd.DataFrame(data)
        csv_buffer = StringIO()  # Create an in-memory buffer to store the CSV data
        df.to_csv(csv_buffer, index=False)

        csv_buffer.seek(0)

        self.s3_client.put_object(
            Body=csv_buffer.getvalue(), Bucket=self.bucket, Key=self.key
        )
        presigned_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": self.key},
            ExpiresIn=settings.S3_LINK_EXPIRY_TIME,
        )

        return presigned_url
