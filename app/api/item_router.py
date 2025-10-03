from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, status
from app.schemas.item import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

# In-memory store
_items: List[Item] = []
_next_id: int = 1

def _next() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid

def _find(item_id: int) -> Optional[Item]:
    for it in _items:
        if it.id == item_id:
            return it
    return None

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    item = Item(id=_next(), name=payload.name, description=payload.description)
    _items.append(item)
    return item

@router.get("/", response_model=List[Item])
def list_items() -> List[Item]:
    return _items

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int = Path(..., ge=1)) -> Item:
    it = _find(item_id)
    if not it:
        raise HTTPException(status_code=404, detail="Item not found")
    return it
