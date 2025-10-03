"""Items API router.

Implements a minimal in-memory CRUD surface to exercise request/response
validation and endpoint wiring without a real database.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.item import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

# In-memory store for demo/testing.
_items: List[Item] = []
_next_id: int = 1


def _next() -> int:
    """Return the next auto-incrementing item identifier.

    Returns:
        int: The next numeric ID.
    """
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid


def _find(item_id: int) -> Optional[Item]:
    """Find an item by ID in the in-memory store.

    Args:
        item_id: Identifier to look up.

    Returns:
        Optional[Item]: The matching item or None.
    """
    for it in _items:
        if it.id == item_id:
            return it
    return None


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    """Create a new item.

    Handles **POST /items/** by validating the request body and appending a new
    in-memory item with a server-assigned ID.

    Args:
        payload: Body containing `name` and `description`.

    Returns:
        Item: The created item, including generated `id`.
    """
    item = Item(id=_next(), name=payload.name, description=payload.description)
    _items.append(item)
    return item


@router.get("/", response_model=List[Item])
def list_items() -> List[Item]:
    """List all items currently stored in memory.

    Returns:
        List[Item]: Items in insertion order.
    """
    return _items


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int = Path(..., ge=1)) -> Item:
    """Fetch a single item by identifier.

    Args:
        item_id: Positive integer item ID.

    Raises:
        HTTPException: 404 if the item cannot be found.

    Returns:
        Item: The matching item.
    """
    it = _find(item_id)
    if not it:
        raise HTTPException(status_code=404, detail="Item not found")
    return it
