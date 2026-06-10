import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    log_id = Column(BigInteger, primary_key=True, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.admin_id"), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(60), nullable=False)
    details = Column(JSONB, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())


class UploadedPDF(Base):
    __tablename__ = "uploaded_pdfs"

    pdf_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.admin_id"), nullable=False)
    filename = Column(String(255), nullable=False)
    upload_path = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class OCRJob(Base):
    __tablename__ = "ocr_jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pdf_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_pdfs.pdf_id"), nullable=False)
    status = Column(String(20), default="PENDING")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_log = Column(Text, nullable=True)


class OCRExtractedRow(Base):
    __tablename__ = "ocr_extracted_rows"

    row_id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("ocr_jobs.job_id"), nullable=False)
    university_name = Column(Text, nullable=False)
    program_name = Column(Text, nullable=False)
    district_name = Column(String(80), nullable=False)
    cutoff_mark = Column(String, nullable=True)
    year = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)