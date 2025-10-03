"""Pydantic schemas for Items."""
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """Shared fields across Item schemas."""
    name: str = Field(..., min_length=1, description="Human-readable name")
    description: str = Field(..., min_length=1, description="Item description")


class ItemCreate(ItemBase):
    """Schema used when creating an item via API."""
    pass


class Item(ItemBase):
    """Schema returned by the API for a stored item.

    Note: Pydantic v2 requires `from_attributes=True` to serialize SQLAlchemy ORM objects.
    """
    id: int = Field(..., ge=1, description="Server-assigned identifier")
    # Enable ORM -> Pydantic conversion (v2 replacement for orm_mode=True)
    model_config = ConfigDict(from_attributes=True)


# Optional alias if any code imports ItemRead as the response model
ItemRead = Item
