import enum
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.generated_spec import GeneratedSpec
    from app.models.knowledge_chunk import KnowledgeChunk
    from app.models.workspace import Workspace


class ProcessingStatus(str, enum.Enum):
    """
    PostgreSQL-backed State Machine transitions for RFP/SRS documents.
    """
    PENDING = "PENDING"          # Uploaded, waiting for worker pickup
    PARSING = "PARSING"          # PyMuPDF extracting text & sections
    EXTRACTING = "EXTRACTING"    # Gemini extracting functional & non-functional requirements
    AUDITING = "AUDITING"        # Risk auditor flagging scope creep & ambiguities (parallel)
    ESTIMATING = "ESTIMATING"    # Effort estimator querying pgvector RAG for cost/hours (parallel)
    COMPLETED = "COMPLETED"      # Full SRS/SOW compiled & validated
    FAILED = "FAILED"            # Failure occurred; error_message populated


class Document(Base, TimestampMixin):
    """
    Document model representing an uploaded RFP or SRS file.
    Tracks state machine lifecycle, extracted content, and compilation output.
    """
    __tablename__ = "documents"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # State Machine Progression
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status_enum", create_type=True),
        default=ProcessingStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Extracted plain text & section metadata
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Diagnostic error details if status == FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="documents")

    generated_specs: Mapped[List["GeneratedSpec"]] = relationship(
        "GeneratedSpec",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    knowledge_chunks: Mapped[List["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
