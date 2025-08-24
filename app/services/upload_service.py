import os
from uuid import UUID, uuid4
import boto3
from typing import Sequence, Any
import boto3.session
from fastapi import UploadFile, HTTPException, status
from sqlmodel import select, Session
from app.models.document import MediaFile
from app.core.config import settings
from fastapi.responses import StreamingResponse

from app.schemas.media import UploadMediaFile

client = boto3.session.Session().client(service_name='s3', aws_access_key_id=settings.R2_ACCESS_KEY_ID, aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY, endpoint_url=settings.R2_ENDPOINT_URL)

def generate_random_file_name(file_name: str) -> str:
    """
    Generate a random file name based on the original file name.
    This can be used to avoid conflicts in file storage.
    """

    base, ext = os.path.splitext(file_name)
    return f"{base}_{uuid4().hex}{ext}"


def create_media_file(db: Session, added_by: UUID, media_file_data: UploadFile, unit_id: UUID | None, project_id: UUID | None, user_id: UUID | None) -> MediaFile:
    """
    Create a new media file record in the database.
    """

    size = media_file_data.size if media_file_data.size else 0
    content_type = media_file_data.content_type if media_file_data.content_type else "application/octet-stream"
    file_name = media_file_data.filename if media_file_data.filename else generate_random_file_name(media_file_data.filename or "")


    client.upload_fileobj(
        media_file_data.file,
        settings.R2_BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType": content_type,
            "ACL": "public-read"  # Adjust ACL as needed
        }
    )

    # Create a MediaFile instance
    media_file = MediaFile(
        file_size=size,
        file_type=content_type,
        file_name=file_name,
        uploaded_by=added_by,
        unit_id=unit_id,
        project_id=project_id,
        file_path=f"{settings.R2_PUBLIC_URL}/{file_name}",
        deleted=False
    )
    db.add(media_file)
    db.commit()
    db.refresh(media_file)
    return media_file

def create_media_files(db: Session, added_by: UUID, media_files: Sequence[UploadFile], unit_id: UUID | None, project_id: UUID | None, user_id: UUID | None) -> Sequence[MediaFile]:
    """
    Create multiple media file records in the database.
    """
    created_files = []
    for media_file in media_files:
        created_file = create_media_file(db, added_by, media_file, unit_id, project_id, user_id)
        created_files.append(created_file)
    return created_files

def get_all_media_files(session: Session) -> Sequence[MediaFile]:
    """
    Retrieve all media files from the database.
    """
    query = select(MediaFile).where(MediaFile.deleted == False)
    media_files = session.exec(query).all()

    return media_files

def get_media_file(session: Session, media_file_id: UUID) -> MediaFile | None:
    """
    Retrieve a media file record by its ID.
    """

    return session.get(MediaFile, media_file_id)


def download_media_file(session: Session, media_file_id: UUID) -> StreamingResponse:
    media_file = get_media_file(session, media_file_id)
    if not media_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    try:
        response = client.get_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=media_file.file_name,
            ResponseContentType=media_file.file_type
        )
        def file_iterator() -> Any:
            while True:
                chunk = response['Body'].read(8192)
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type=media_file.file_type,
            headers={"Content-Disposition": f'attachment; filename="{media_file.file_name}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error downloading file")