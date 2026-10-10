import uuid
import enum
from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from src.vaultapi.models.base import Base


class ShareRole(str, enum.Enum):
    VIEWER = "viewer"
    EDITOR = "editor"


class DocumentShare(Base):
    __tablename__ = "document_shares"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[ShareRole] = mapped_column(SQLEnum(ShareRole), nullable=False)
