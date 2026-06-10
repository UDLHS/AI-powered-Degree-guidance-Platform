from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import os
import shutil
from uuid import uuid4

from fastapi import UploadFile, File
from app.models.admin import UploadedPDF, OCRJob, AdminAuditLog
from app.database import get_db
from app.models.user import User
from app.models.admin import Admin
from app.models.academic import (
    AcademicProfile,
    ProfileInterest,
    FieldOfInterest,
    District,
    RecommendationResult
)
from app.models.university import University, DegreeProgram, CutoffMark
from app.utils.security import verify_password, create_access_token, get_current_admin
from datetime import datetime, timezone
from app.models.admin import UploadedPDF, OCRJob, OCRExtractedRow, AdminAuditLog
from decimal import Decimal, InvalidOperation
from typing import Optional

from app.models.academic import District
from pydantic import BaseModel

router = APIRouter()

class OCRExtractedRowUpdateRequest(BaseModel):
    university_name: Optional[str] = None
    program_name: Optional[str] = None
    district_name: Optional[str] = None
    cutoff_mark: Optional[str] = None
    year: Optional[str] = None
    is_verified: Optional[bool] = None
def get_next_id(db: Session, model, column):
    current_max = db.query(func.max(column)).scalar()
    return 1 if current_max is None else current_max + 1

@router.post("/token")
def admin_login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == form_data.username).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin email or password"
        )

    if not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin email or password"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    access_token = create_access_token(
        data={
            "sub": str(admin.admin_id),
            "email": admin.email,
            "role": "admin"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_admin_profile(
    current_admin: Admin = Depends(get_current_admin)
):
    return {
        "admin_id": str(current_admin.admin_id),
        "name": current_admin.name,
        "email": current_admin.email,
        "is_active": current_admin.is_active,
        "created_at": current_admin.created_at
    }


@router.get("/metrics")
def get_admin_metrics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_profiles = db.query(AcademicProfile).count()
    total_universities = db.query(University).count()
    total_degree_programs = db.query(DegreeProgram).count()
    total_recommendation_results = db.query(RecommendationResult).count()

    average_z_score = db.query(
        func.avg(AcademicProfile.z_score)
    ).scalar()

    district_rows = (
        db.query(
            District.district_name,
            func.count(AcademicProfile.profile_id).label("profile_count")
        )
        .join(AcademicProfile, AcademicProfile.district_id == District.district_id)
        .group_by(District.district_name)
        .order_by(desc("profile_count"))
        .all()
    )

    popular_field_rows = (
        db.query(
            FieldOfInterest.field_name,
            FieldOfInterest.category,
            func.count(ProfileInterest.field_id).label("interest_count")
        )
        .join(ProfileInterest, ProfileInterest.field_id == FieldOfInterest.field_id)
        .group_by(FieldOfInterest.field_name, FieldOfInterest.category)
        .order_by(desc("interest_count"))
        .all()
    )

    return {
        "admin": {
            "admin_id": str(current_admin.admin_id),
            "name": current_admin.name,
            "email": current_admin.email
        },
        "summary": {
            "total_users": total_users,
            "total_academic_profiles": total_profiles,
            "total_universities": total_universities,
            "total_degree_programs": total_degree_programs,
            "total_recommendation_results": total_recommendation_results,
            "average_z_score": round(float(average_z_score), 4) if average_z_score else 0
        },
        "district_distribution": [
            {
                "district_name": row.district_name,
                "profile_count": row.profile_count
            }
            for row in district_rows
        ],
        "popular_fields_of_interest": [
            {
                "field_name": row.field_name,
                "category": row.category,
                "interest_count": row.interest_count
            }
            for row in popular_field_rows
        ]
    }

@router.post("/upload-handbook")
def upload_handbook_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    upload_dir = "uploads/handbooks"
    os.makedirs(upload_dir, exist_ok=True)

    unique_filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    uploaded_pdf = UploadedPDF(
        admin_id=current_admin.admin_id,
        filename=file.filename,
        upload_path=file_path,
        status="PENDING"
    )

    db.add(uploaded_pdf)
    db.commit()
    db.refresh(uploaded_pdf)

    ocr_job = OCRJob(
        pdf_id=uploaded_pdf.pdf_id,
        status="PENDING"
    )

    db.add(ocr_job)

    audit_log = AdminAuditLog(
        admin_id=current_admin.admin_id,
        action="UPLOAD_HANDBOOK",
        entity_type="UploadedPDF",
        details={
            "pdf_id": str(uploaded_pdf.pdf_id),
            "filename": file.filename,
            "upload_path": file_path
        }
    )

    db.add(audit_log)
    db.commit()
    db.refresh(ocr_job)

    return {
        "message": "PDF uploaded successfully. OCR job created.",
        "pdf": {
            "pdf_id": str(uploaded_pdf.pdf_id),
            "filename": uploaded_pdf.filename,
            "upload_path": uploaded_pdf.upload_path,
            "status": uploaded_pdf.status,
            "uploaded_at": uploaded_pdf.uploaded_at
        },
        "ocr_job": {
            "job_id": str(ocr_job.job_id),
            "status": ocr_job.status
        }
    }

@router.get("/uploaded-pdfs")
def get_uploaded_pdfs(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    pdfs = (
        db.query(UploadedPDF)
        .order_by(UploadedPDF.uploaded_at.desc())
        .all()
    )

    return [
        {
            "pdf_id": str(pdf.pdf_id),
            "admin_id": str(pdf.admin_id),
            "filename": pdf.filename,
            "upload_path": pdf.upload_path,
            "status": pdf.status,
            "uploaded_at": pdf.uploaded_at
        }
        for pdf in pdfs
    ]


@router.get("/ocr-jobs")
def get_ocr_jobs(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    jobs = (
        db.query(OCRJob, UploadedPDF)
        .join(UploadedPDF, OCRJob.pdf_id == UploadedPDF.pdf_id)
        .order_by(OCRJob.started_at.desc().nullslast())
        .all()
    )

    return [
        {
            "job_id": str(job.job_id),
            "pdf_id": str(pdf.pdf_id),
            "filename": pdf.filename,
            "pdf_status": pdf.status,
            "job_status": job.status,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error_log": job.error_log
        }
        for job, pdf in jobs
    ]




@router.post("/ocr-jobs/{job_id}/process")
def process_ocr_job_mock(
    job_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    ocr_job = db.query(OCRJob).filter(OCRJob.job_id == job_id).first()

    if not ocr_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR job not found"
        )

    uploaded_pdf = (
        db.query(UploadedPDF)
        .filter(UploadedPDF.pdf_id == ocr_job.pdf_id)
        .first()
    )

    if not uploaded_pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded PDF not found"
        )

    # Delete old mock extracted rows if this job was processed before
    db.query(OCRExtractedRow).filter(
        OCRExtractedRow.job_id == ocr_job.job_id
    ).delete()

    ocr_job.status = "PROCESSING"
    ocr_job.started_at = datetime.now(timezone.utc)
    uploaded_pdf.status = "PROCESSING"
    db.commit()

    # Mock OCR extracted rows
    # Later, real OCR will replace this section.
    mock_rows = [
        {
            "university_name": "University of Colombo",
            "program_name": "BSc in Computer Science",
            "district_name": "Colombo",
            "cutoff_mark": "1.6500",
            "year": "2024"
        },
        {
            "university_name": "University of Moratuwa",
            "program_name": "BSc Engineering",
            "district_name": "Colombo",
            "cutoff_mark": "1.9000",
            "year": "2024"
        },
        {
            "university_name": "University of Kelaniya",
            "program_name": "BSc in Physical Science",
            "district_name": "Colombo",
            "cutoff_mark": "1.4500",
            "year": "2024"
        },
        {
            "university_name": "University of Kelaniya",
            "program_name": "Bachelor of Commerce",
            "district_name": "Colombo",
            "cutoff_mark": "1.3000",
            "year": "2024"
        }
    ]

    next_row_id = get_next_id(db, OCRExtractedRow, OCRExtractedRow.row_id)

    for index, row in enumerate(mock_rows):
        db.add(
            OCRExtractedRow(
                row_id=next_row_id + index,
                job_id=ocr_job.job_id,
                university_name=row["university_name"],
                program_name=row["program_name"],
                district_name=row["district_name"],
                cutoff_mark=row["cutoff_mark"],
                year=row["year"],
                is_verified=False
            )
        )

    ocr_job.status = "DONE"
    ocr_job.completed_at = datetime.now(timezone.utc)
    ocr_job.error_log = None
    uploaded_pdf.status = "DONE"

    audit_log = AdminAuditLog(
        log_id=get_next_id(db, AdminAuditLog, AdminAuditLog.log_id),
        admin_id=current_admin.admin_id,
        action="PROCESS_OCR_JOB",
        entity_type="OCRJob",
        details={
            "job_id": str(ocr_job.job_id),
            "pdf_id": str(uploaded_pdf.pdf_id),
            "mock_rows_created": len(mock_rows)
        }
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "Mock OCR processing completed successfully.",
        "job_id": str(ocr_job.job_id),
        "pdf_id": str(uploaded_pdf.pdf_id),
        "filename": uploaded_pdf.filename,
        "status": ocr_job.status,
        "rows_extracted": len(mock_rows)
    }





@router.get("/ocr-jobs/{job_id}/extracted-rows")
def get_ocr_extracted_rows(
    job_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    ocr_job = db.query(OCRJob).filter(OCRJob.job_id == job_id).first()

    if not ocr_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR job not found"
        )

    rows = (
        db.query(OCRExtractedRow)
        .filter(OCRExtractedRow.job_id == job_id)
        .order_by(OCRExtractedRow.row_id)
        .all()
    )

    return {
        "job_id": str(job_id),
        "job_status": ocr_job.status,
        "total_rows": len(rows),
        "rows": [
            {
                "row_id": row.row_id,
                "university_name": row.university_name,
                "program_name": row.program_name,
                "district_name": row.district_name,
                "cutoff_mark": row.cutoff_mark,
                "year": row.year,
                "is_verified": row.is_verified
            }
            for row in rows
        ]
    }


@router.get("/ocr-extracted-rows/pending")
def get_pending_ocr_rows(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    rows = (
        db.query(OCRExtractedRow)
        .filter(OCRExtractedRow.is_verified == False)
        .order_by(OCRExtractedRow.row_id)
        .all()
    )

    return {
        "total_pending_rows": len(rows),
        "rows": [
            {
                "row_id": row.row_id,
                "job_id": str(row.job_id),
                "university_name": row.university_name,
                "program_name": row.program_name,
                "district_name": row.district_name,
                "cutoff_mark": row.cutoff_mark,
                "year": row.year,
                "is_verified": row.is_verified
            }
            for row in rows
        ]
    }


@router.patch("/ocr-extracted-rows/{row_id}")
def update_ocr_extracted_row(
    row_id: int,
    payload: OCRExtractedRowUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    row = (
        db.query(OCRExtractedRow)
        .filter(OCRExtractedRow.row_id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR extracted row not found"
        )

    if payload.university_name is not None:
        row.university_name = payload.university_name

    if payload.program_name is not None:
        row.program_name = payload.program_name

    if payload.district_name is not None:
        row.district_name = payload.district_name

    if payload.cutoff_mark is not None:
        row.cutoff_mark = payload.cutoff_mark

    if payload.year is not None:
        row.year = payload.year

    if payload.is_verified is not None:
        row.is_verified = payload.is_verified

    audit_log = AdminAuditLog(
        log_id=get_next_id(db, AdminAuditLog, AdminAuditLog.log_id),
        admin_id=current_admin.admin_id,
        action="UPDATE_OCR_EXTRACTED_ROW",
        entity_type="OCRExtractedRow",
        details={
            "row_id": row.row_id,
            "job_id": str(row.job_id)
        }
    )

    db.add(audit_log)
    db.commit()
    db.refresh(row)

    return {
        "message": "OCR extracted row updated successfully.",
        "row": {
            "row_id": row.row_id,
            "job_id": str(row.job_id),
            "university_name": row.university_name,
            "program_name": row.program_name,
            "district_name": row.district_name,
            "cutoff_mark": row.cutoff_mark,
            "year": row.year,
            "is_verified": row.is_verified
        }
    }

@router.patch("/ocr-extracted-rows/{row_id}/verify")
def verify_ocr_extracted_row(
    row_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    row = (
        db.query(OCRExtractedRow)
        .filter(OCRExtractedRow.row_id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR extracted row not found"
        )

    row.is_verified = True

    audit_log = AdminAuditLog(
        log_id=get_next_id(db, AdminAuditLog, AdminAuditLog.log_id),
        admin_id=current_admin.admin_id,
        action="VERIFY_OCR_EXTRACTED_ROW",
        entity_type="OCRExtractedRow",
        details={
            "row_id": row.row_id,
            "job_id": str(row.job_id)
        }
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "OCR extracted row verified successfully.",
        "row_id": row.row_id,
        "is_verified": row.is_verified
    }


@router.post("/ocr-jobs/{job_id}/approve-to-cutoffs")
def approve_ocr_rows_to_cutoff_marks(
    job_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    ocr_job = db.query(OCRJob).filter(OCRJob.job_id == job_id).first()

    if not ocr_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR job not found"
        )

    verified_rows = (
        db.query(OCRExtractedRow)
        .filter(OCRExtractedRow.job_id == job_id)
        .filter(OCRExtractedRow.is_verified == True)
        .all()
    )

    if not verified_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verified OCR rows found for this job"
        )

    inserted_count = 0
    updated_count = 0
    skipped_rows = []

    for row in verified_rows:
        try:
            cutoff_value = Decimal(str(row.cutoff_mark))
            year_value = int(row.year)
        except (InvalidOperation, ValueError, TypeError):
            skipped_rows.append({
                "row_id": row.row_id,
                "reason": "Invalid cutoff mark or year"
            })
            continue

        university = (
            db.query(University)
            .filter(University.name.ilike(row.university_name.strip()))
            .first()
        )

        if not university:
            skipped_rows.append({
                "row_id": row.row_id,
                "reason": "University not found"
            })
            continue

        program = (
            db.query(DegreeProgram)
            .filter(DegreeProgram.university_id == university.university_id)
            .filter(DegreeProgram.program_name.ilike(row.program_name.strip()))
            .first()
        )

        if not program:
            skipped_rows.append({
                "row_id": row.row_id,
                "reason": "Degree program not found"
            })
            continue

        district = (
            db.query(District)
            .filter(District.district_name.ilike(row.district_name.strip()))
            .first()
        )

        if not district:
            skipped_rows.append({
                "row_id": row.row_id,
                "reason": "District not found"
            })
            continue

        existing_cutoff = (
            db.query(CutoffMark)
            .filter(CutoffMark.program_id == program.program_id)
            .filter(CutoffMark.district_id == district.district_id)
            .filter(CutoffMark.year == year_value)
            .first()
        )

        if existing_cutoff:
            existing_cutoff.min_cutoff_mark = cutoff_value
            updated_count += 1
        else:
            new_cutoff = CutoffMark(
                program_id=program.program_id,
                district_id=district.district_id,
                year=year_value,
                min_cutoff_mark=cutoff_value
            )

            db.add(new_cutoff)
            inserted_count += 1

    audit_log = AdminAuditLog(
        log_id=get_next_id(db, AdminAuditLog, AdminAuditLog.log_id),
        admin_id=current_admin.admin_id,
        action="APPROVE_OCR_ROWS_TO_CUTOFFS",
        entity_type="CutoffMark",
        details={
            "job_id": str(job_id),
            "verified_rows": len(verified_rows),
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "skipped_count": len(skipped_rows)
        }
    )

    db.add(audit_log)
    db.commit()

    return {
        "message": "Verified OCR rows processed into cutoff marks.",
        "job_id": str(job_id),
        "verified_rows": len(verified_rows),
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": len(skipped_rows),
        "skipped_rows": skipped_rows
    }