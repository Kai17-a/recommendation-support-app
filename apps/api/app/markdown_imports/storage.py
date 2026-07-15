from typing import Protocol

import boto3

from app.core.config import settings


class MarkdownObjectStorage(Protocol):
    def put(self, key: str, data: bytes) -> None: ...

    def get(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None: ...


class S3MarkdownObjectStorage:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None,
        region: str,
        access_key_id: str | None,
        secret_access_key: str | None,
        server_side_encryption: str | None,
    ) -> None:
        self.bucket = bucket
        self.server_side_encryption = server_side_encryption
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def put(self, key: str, data: bytes) -> None:
        encryption = (
            {"ServerSideEncryption": self.server_side_encryption}
            if self.server_side_encryption
            else {}
        )
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType="text/markdown; charset=utf-8",
            **encryption,
        )

    def get(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def get_markdown_object_storage() -> MarkdownObjectStorage:
    return S3MarkdownObjectStorage(
        bucket=settings.s3_markdown_bucket,
        endpoint_url=settings.s3_endpoint_url,
        region=settings.s3_region,
        access_key_id=settings.s3_access_key_id,
        secret_access_key=settings.s3_secret_access_key,
        server_side_encryption=settings.s3_server_side_encryption,
    )
