from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)

class Item(BaseModel):
    id: int
    name: str
    description: str

    # allow constructing from ORM objects later (SQLAlchemy)
    model_config = {"from_attributes": True}
