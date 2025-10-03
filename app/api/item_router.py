# app/api/item_router.py
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.item import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

# --- In-memory "database" ---
_items: List[Item] = []
_next_id: int = 1


def _get_next_id() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid


def _find_item(item_id: int) -> Optional[Item]:
    for it in _items:
        if it.id == item_id:
            return it
    return None


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    item = Item(id=_get_next_id(), name=payload.name, description=payload.description)
    _items.append(item)
    return item


@router.get("/", response_model=List[Item])
def list_items() -> List[Item]:
    return _items


@router.get("/{item_id}", response_model=Item)
def get_item(
    item_id: int = Path(..., ge=1, description="ID of the item to fetch"),
) -> Item:
    item = _find_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
