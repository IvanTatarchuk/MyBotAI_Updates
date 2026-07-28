from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.core.security import get_api_key_dependency
from app.services.analysis import analyze_file


router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    _: str = Depends(get_api_key_dependency),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    content = await file.read()
    result = analyze_file(filename=file.filename, content_bytes=content)
    return {"filename": file.filename, "analysis": result}

