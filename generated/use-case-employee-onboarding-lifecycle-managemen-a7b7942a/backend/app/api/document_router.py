from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from app.schemas.document import DocumentRead, DocumentCreate
from app.services.document_service import DocumentService
from app.api.auth_router import get_current_user, User

router = APIRouter()

@router.get("/employee/{employee_id}", response_model=List[DocumentRead])
async def get_documents(employee_id: int, current_user: User = Depends(get_current_user)):
    if not current_user.can_access_employee(employee_id):
        raise HTTPException(status_code=403, detail="Not authorized to view documents.")
    docs = await DocumentService.get_documents(employee_id)
    return docs

@router.post("/employee/{employee_id}", response_model=DocumentRead)
async def upload_document(employee_id: int, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    # Employees and HR admin can upload
    if not current_user.can_access_employee(employee_id):
        raise HTTPException(status_code=403, detail="Not authorized to upload documents.")
    doc = await DocumentService.upload_document(employee_id, file)
    return doc

@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: int, current_user: User = Depends(get_current_user)):
    deleted = await DocumentService.delete_document(document_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")
    return None
