from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from src.vaultapi.models.document import Document
from src.vaultapi.models.document_share import DocumentShare, ShareRole
from src.vaultapi.models.user import User
from src.vaultapi.schemas.document import DocumentResponse, DocumentShareResponse
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

    is_owner = str(document.owner_id) == owner_id

    if not is_owner:
        share_result = await db.execute(
            select(DocumentShare).where(
                DocumentShare.document_id == document_id,
                DocumentShare.user_id == owner_id,
            )
        )
        share = share_result.scalar_one_or_none()
        if not share:
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


async def share_document(
    db: AsyncSession, document_id: str, owner_id: str, target_email: str, role: str
) -> DocumentShareResponse:
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    document = doc_result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if str(document.owner_id) != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the document owner can share this document",
        )

    user_result = await db.execute(select(User).where(User.email == target_email))
    target_user = user_result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found"
        )

    existing_share = await db.execute(
        select(DocumentShare).where(
            DocumentShare.document_id == document_id,
            DocumentShare.user_id == target_user.id,
        )
    )

    if existing_share.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already shared with this user",
        )

    new_share = DocumentShare(
        document_id=document_id, user_id=target_user.id, role=role
    )

    db.add(new_share)
    await db.commit()
    await db.refresh(new_share)

    return DocumentShareResponse(
        id=new_share.id,
        document_id=new_share.document_id,
        user_id=new_share.user_id,
        role=new_share.role,
    )


async def update_document(
    db: AsyncSession, document_id: str, user_id: str, content: str
) -> DocumentResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    is_owner = str(document.owner_id) == user_id

    if not is_owner:
        share_result = await db.execute(
            select(DocumentShare).where(
                DocumentShare.document_id == document_id,
                DocumentShare.user_id == user_id,
                DocumentShare.role == ShareRole.EDITOR,
            )
        )
        share = share_result.scalar_one_or_none()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this document",
            )

    encrypted_content = encrypt_data(content)
    document.encrypted_content = encrypted_content

    await db.commit()
    await db.refresh(document)

    return DocumentResponse(
        id=document.id,
        title=document.title,
        content=content,
        owner_id=document.owner_id,
        created_at=document.created_at,
    )
