from typing import TYPE_CHECKING, List
from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.knowledge_chunk import KnowledgeChunk


class Workspace(Base, TimestampMixin):
    """
    Workspace model enforcing multi-tenancy.
    Groups documents, past project benchmarks, rate cards, and team members.
    """
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    
    # Default agency hourly billing rate for effort/cost calculations ($/hr)
    default_hourly_rate: Mapped[float] = mapped_column(Float, default=150.0, nullable=False)

    # Relationships
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    knowledge_chunks: Mapped[List["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
