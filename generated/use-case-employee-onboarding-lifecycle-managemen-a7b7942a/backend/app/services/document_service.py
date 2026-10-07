from typing import List, Optional
from app.schemas.document import DocumentRead
from fastapi import UploadFile
from datetime import datetime
import uuid
import os
from app.api.auth_router import User

# Dummy storage
_documents = {}
_doc_id_seq = 1

# For demo, store uploaded files in a temp subfolder
STORAGE_DIR = "./storage"

os.makedirs(STORAGE_DIR, exist_ok=True)

class DocumentService:

    @staticmethod
    async def get_documents(employee_id: int) -> List[DocumentRead]:
        docs = [doc for doc in _documents.values() if doc["employee_id"] == employee_id]
        return [DocumentRead(**doc) for doc in docs]

    @staticmethod
    async def upload_document(employee_id: int, upload_file: UploadFile) -> DocumentRead:
        global _doc_id_seq
        doc_id = _doc_id_seq
        _doc_id_seq += 1
        filename = f"{uuid.uuid4()}_{upload_file.filename}"
        filepath = os.path.join(STORAGE_DIR, filename)
        # Save file asynchronously
        contents = await upload_file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        doc = {
            "document_id": doc_id,
            "employee_id": employee_id,
            "document_name": upload_file.filename,
            "upload_date": datetime.utcnow(),
            "file_url": f"/storage/{filename}"
        }
        _documents[doc_id] = doc
        return DocumentRead(**doc)

    @staticmethod
    async def delete_document(document_id: int, user: User) -> bool:
        doc = _documents.get(document_id)
        if not doc:
            return False
        # Check user permission
        if not user.can_access_employee(doc["employee_id"]):
            return False
        # Delete from disk
        filename = doc["file_url"].replace("/storage/", "")
        filepath = os.path.join(STORAGE_DIR, filename)
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass
        del _documents[document_id]
        return True
