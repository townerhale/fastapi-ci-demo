# app/api/item_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.item import Item as ItemORM
from app.schemas.item import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> Item:
    """
    Create a new Item row and return it.
    """
    obj = ItemORM(name=payload.name, description=payload.description)
    db.add(obj)
    db.commit()
    db.refresh(obj)  # populate auto-generated fields (e.g., id)
    return Item.model_validate(obj)


@router.get("/", response_model=List[Item])
def read_items(db: Session = Depends(get_db)) -> List[Item]:
    """
    List all items.
    """
    result = db.execute(select(ItemORM))
    rows = result.scalars().all()
    return [Item.model_validate(r) for r in rows]


@router.get("/{item_id}", response_model=Item)
def read_item(
    item_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> Item:
    """
    Get a single item by ID.
    """
    obj = db.get(ItemORM, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item.model_validate(obj)
