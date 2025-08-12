from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import uuid
import os

from sqlmodel import Session
from app.auth.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import Role, User
from app.schemas.media import MediaFileReadSchema
from app.services.upload_service import create_media_file, create_media_files, download_media_file, get_all_media_files, get_media_file

router = APIRouter()

@router.post("/upload-media/", dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
async def upload_media(file: UploadFile = File(...), current_user: User = Depends(get_current_user()), session: Session = Depends(get_session)):

    return create_media_file(session, current_user.id, file)

@router.post("/upload-multiple-media/", dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
async def upload_multiple_media(files: list[UploadFile] = File(...), current_user: User = Depends(get_current_user()), session: Session = Depends(get_session)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    return create_media_files(session, current_user.id, files)

@router.get("/media", response_model=list[MediaFileReadSchema], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
async def get_all_media(session: Session = Depends(get_session)):
    return get_all_media_files(session)


@router.get("/media/{media_id}", response_model=MediaFileReadSchema, dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
async def get_media(media_id: uuid.UUID, session: Session = Depends(get_session)):
    return get_media_file(session, media_id)


@router.get("/media/download/{media_id}", dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
async def download_media(media_id: uuid.UUID, session: Session = Depends(get_session)):
    return download_media_file(session, media_id)