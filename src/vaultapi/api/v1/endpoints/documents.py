from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.vaultapi.db.session import get_db
from src.vaultapi.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentShareCreate,
    DocumentShareResponse,
    DocumentUpdate,
)
from src.vaultapi.services.document import (
    create_document,
    get_document,
    share_document,
    update_document,
)
from src.vaultapi.core.deps import get_current_user
from src.vaultapi.models.user import User
from uuid import UUID

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # The service now returns the fully mapped DocumentResponse
    return await create_document(
        db, str(current_user.id), document_data.title, document_data.content
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_document(db, str(document_id), str(current_user.id))


@router.post(
    "/{document_id}/share",
    response_model=DocumentShareResponse,
    status_code=status.HTTP_201_CREATED,
)
async def share_document_endpoint(
    document_id: UUID,
    share_data: DocumentShareCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await share_document(
        db, str(document_id), str(current_user.id), share_data.email, share_data.role
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_existing_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_document(
        db, str(document_id), str(current_user.id), document_data.content
    )
