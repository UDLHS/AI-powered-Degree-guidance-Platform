from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.academic import AcademicProfile, ProfileSubject, ProfileInterest
from app.schemas.profile_schema import AcademicProfileCreateRequest, AcademicProfileCreateResponse
from app.utils.security import get_current_user

from app.database import get_db
from app.models.academic import (
    ALevelStream,
    Subject,
    District,
    FieldOfInterest
)

router = APIRouter()


@router.get("/streams")
def get_streams(db: Session = Depends(get_db)):
    streams = db.query(ALevelStream).order_by(ALevelStream.stream_id).all()

    return [
        {
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "description": stream.description
        }
        for stream in streams
    ]


@router.get("/streams/{stream_id}/subjects")
def get_subjects_by_stream(
    stream_id: int,
    db: Session = Depends(get_db)
):
    subjects = (
        db.query(Subject)
        .filter(Subject.stream_id == stream_id)
        .order_by(Subject.subject_name)
        .all()
    )

    return [
        {
            "subject_id": subject.subject_id,
            "stream_id": subject.stream_id,
            "subject_name": subject.subject_name
        }
        for subject in subjects
    ]


@router.get("/districts")
def get_districts(db: Session = Depends(get_db)):
    districts = db.query(District).order_by(District.district_name).all()

    return [
        {
            "district_id": district.district_id,
            "district_name": district.district_name,
            "province": district.province
        }
        for district in districts
    ]


@router.get("/fields-of-interest")
def get_fields_of_interest(db: Session = Depends(get_db)):
    fields = db.query(FieldOfInterest).order_by(FieldOfInterest.field_name).all()

    return [
        {
            "field_id": field.field_id,
            "field_name": field.field_name,
            "category": field.category
        }
        for field in fields
    ]

@router.post("/", response_model=AcademicProfileCreateResponse)
def create_academic_profile(
    payload: AcademicProfileCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if len(set(payload.subject_ids)) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subjects must be three different subjects"
        )

    # Check selected subjects belong to selected stream
    subjects = (
        db.query(Subject)
        .filter(Subject.subject_id.in_(payload.subject_ids))
        .all()
    )

    if len(subjects) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more subjects are invalid"
        )

    for subject in subjects:
        if subject.stream_id != payload.stream_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected subjects must belong to the selected stream"
            )

    # Check district exists
    district = (
        db.query(District)
        .filter(District.district_id == payload.district_id)
        .first()
    )

    if not district:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid district"
        )

    # Create academic profile
    profile = AcademicProfile(
        user_id=current_user.user_id,
        stream_id=payload.stream_id,
        district_id=payload.district_id,
        z_score=payload.z_score
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Save 3 subjects
    for index, subject_id in enumerate(payload.subject_ids, start=1):
        db.add(
            ProfileSubject(
                profile_id=profile.profile_id,
                subject_id=subject_id,
                slot_position=index
            )
        )

    # Save fields of interest
    for field_id in payload.field_ids:
        db.add(
            ProfileInterest(
                profile_id=profile.profile_id,
                field_id=field_id
            )
        )

    db.commit()

    return {
        "profile_id": str(profile.profile_id),
        "user_id": str(current_user.user_id),
        "stream_id": profile.stream_id,
        "district_id": profile.district_id,
        "z_score": float(profile.z_score),
        "subject_ids": payload.subject_ids,
        "field_ids": payload.field_ids,
        "message": "Academic profile created successfully"
    }