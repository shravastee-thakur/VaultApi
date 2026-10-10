from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    content: str
    owner_id: UUID
    created_at: datetime
    model_config = {"from_attributes": True}


class DocumentShareCreate(BaseModel):
    email: EmailStr
    role: str = Field(pattern="^(viewer|editor)$")


class DocumentShareResponse(BaseModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    role: str
    model_config = {"from_attributes": True}


class DocumentUpdate(BaseModel):
    content: str = Field(min_length=1)
