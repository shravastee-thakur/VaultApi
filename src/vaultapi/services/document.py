from sqlalchemy.ext.asyncio import AsyncSession
from src.vaultapi.models.document import Document
from src.vaultapi.core.encryption import encrypt_data


async def create_document(db: AsyncSession, owner_id: str, title: str, content: str):
    encrypted_content = encrypt_data(content)

    new_document = Document(
        title=title, encrypted_content=encrypted_content, owner_id=owner_id
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    return new_document
