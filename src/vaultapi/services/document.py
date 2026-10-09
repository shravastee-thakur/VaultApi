from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from src.vaultapi.models.document import Document
from src.vaultapi.schemas.document import DocumentResponse
from src.vaultapi.core.encryption import encrypt_data, decrypt_data


async def create_document(
    db: AsyncSession, owner_id: str, title: str, content: str
) -> DocumentResponse:
    # 1. Encrypt the data
    encrypted_content = encrypt_data(content)

    # 2. Save to database
    new_document = Document(
        title=title, encrypted_content=encrypted_content, owner_id=owner_id
    )
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    # 3. Construct and return the Pydantic schema
    # We pass the original unencrypted 'content' back so the user can see it
    return DocumentResponse(
        id=new_document.id,
        title=new_document.title,
        content=content,
        owner_id=new_document.owner_id,
        created_at=new_document.created_at,
    )


async def get_document(
    db: AsyncSession, document_id: str, owner_id: str
) -> DocumentResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if str(document.owner_id) != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this document",
        )

    decrypted_content = decrypt_data(document.encrypted_content)

    return DocumentResponse(
        id=document.id,
        title=document.title,
        content=decrypted_content,
        owner_id=document.owner_id,
        created_at=document.created_at,
    )
