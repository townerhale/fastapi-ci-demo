from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Item(Base):
    """SQLAlchemy ORM model for items."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, name={self.name!r})"
