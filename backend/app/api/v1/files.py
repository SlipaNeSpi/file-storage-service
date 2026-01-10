from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.services.file_service import FileService
from app.middleware.auth import get_current_user
from app.database import get_db
import io

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", summary="Upload a file")
async def upload_file(
        file: UploadFile = File(...),
        folder: str = Query("root"),
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Upload a file to storage.
    Max size: 1GB
    """
    try:
        service = FileService(db)
        result = await service.upload_file(current_user['sub'], file, folder)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", summary="List user files")
async def list_files(
        folder: str = Query("root"),
        skip: int = Query(0),
        limit: int = Query(20),
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get list of user's files"""
    service = FileService(db)
    files = service.get_user_files(current_user['sub'], folder, skip, limit)
    return files


@router.get("/{file_id}/download", summary="Download file")
async def download_file(
        file_id: str,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Download a file"""
    try:
        service = FileService(db)
        file_data, filename = await service.download_file(file_id, current_user['sub'])

        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{file_id}", summary="Delete file")
async def delete_file(
        file_id: str,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Delete a file"""
    try:
        service = FileService(db)
        result = await service.delete_file(file_id, current_user['sub'])
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{file_id}", summary="Rename file")
async def rename_file(
        file_id: str,
        new_name: str = Query(...),
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Rename a file"""
    try:
        service = FileService(db)
        result = await service.rename_file(file_id, new_name, current_user['sub'])
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{file_id}/metadata", summary="Get file metadata")
async def get_file_metadata(
        file_id: str,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get file metadata"""
    try:
        service = FileService(db)
        metadata = service.get_file_metadata(file_id, current_user['sub'])
        return metadata
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
