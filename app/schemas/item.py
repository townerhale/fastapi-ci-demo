"""Pydantic schemas for Items."""

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Shared fields across Item schemas."""

    name: str = Field(..., min_length=1, description="Human-readable name")
    description: str = Field(..., min_length=1, description="Item description")


class ItemCreate(ItemBase):
    """Schema used when creating an item via API."""
    pass


class Item(ItemBase):
    """Schema returned by the API for a stored item."""

    id: int = Field(..., ge=1, description="Server-assigned identifier")
