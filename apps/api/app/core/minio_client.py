"""
AxonBridge — MinIO Object Storage Client

Client for screenshot audit storage, document management,
and clinical artifact archival.
"""

from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# MinIO client instance
_minio_client: Minio | None = None


def get_minio_client() -> Minio:
    """Get or create the MinIO client."""
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
    return _minio_client


async def ensure_buckets() -> None:
    """Create required MinIO buckets if they don't exist."""
    client = get_minio_client()
    buckets = [
        settings.MINIO_BUCKET_SCREENSHOTS,
        settings.MINIO_BUCKET_DOCUMENTS,
    ]

    for bucket_name in buckets:
        try:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info("minio_bucket_created", bucket=bucket_name)
        except S3Error as e:
            logger.error("minio_bucket_error", bucket=bucket_name, error=str(e))
            raise


def upload_file(
    bucket: str,
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file to MinIO.
    Returns the object path.
    """
    client = get_minio_client()
    stream = BytesIO(data)

    client.put_object(
        bucket,
        object_name,
        stream,
        length=len(data),
        content_type=content_type,
    )

    logger.info(
        "minio_file_uploaded",
        bucket=bucket,
        object_name=object_name,
        size_bytes=len(data),
    )

    return f"{bucket}/{object_name}"


def upload_screenshot(
    object_name: str,
    data: bytes,
) -> str:
    """Upload an audit screenshot."""
    return upload_file(
        bucket=settings.MINIO_BUCKET_SCREENSHOTS,
        object_name=object_name,
        data=data,
        content_type="image/png",
    )


def download_file(bucket: str, object_name: str) -> bytes:
    """Download a file from MinIO."""
    client = get_minio_client()
    response = client.get_object(bucket, object_name)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def get_presigned_url(
    bucket: str,
    object_name: str,
    expires_hours: int = 1,
) -> str:
    """Generate a presigned URL for temporary access."""
    from datetime import timedelta

    client = get_minio_client()
    return client.presigned_get_object(
        bucket,
        object_name,
        expires=timedelta(hours=expires_hours),
    )


def delete_file(bucket: str, object_name: str) -> None:
    """Delete a file from MinIO."""
    client = get_minio_client()
    client.remove_object(bucket, object_name)
    logger.info("minio_file_deleted", bucket=bucket, object_name=object_name)


async def check_minio_health() -> bool:
    """Verify MinIO connectivity."""
    try:
        client = get_minio_client()
        client.list_buckets()
        return True
    except Exception:
        return False
