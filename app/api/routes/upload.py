from fastapi import APIRouter, UploadFile, File
import uuid
import os

router = APIRouter()

UPLOAD_DIR = "uploaded_artworks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-artwork/")
async def upload_artwork(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"filename": filename, "url": f"/{UPLOAD_DIR}/{filename}"}