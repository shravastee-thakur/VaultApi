from pydantic import BaseModel, Field
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
