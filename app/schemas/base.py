"""Shared Pydantic base schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DBSchema(BaseModel):
    """Base for all schemas returned from the database."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
