from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.academic import (
    ALevelStream,
    Subject,
    District,
    FieldOfInterest,
    AcademicProfile,
    ProfileSubject,
    ProfileInterest,
    RecommendationResult,
)
from app.schemas.profile_schema import (
    AcademicProfileCreateRequest,
    AcademicProfileCreateResponse,
)
from app.utils.security import get_current_user
from app.services.activity_service import log_student_activity


router = APIRouter()


def build_profile_response(db: Session, profile: AcademicProfile):
    subjects = (
        db.query(ProfileSubject, Subject)
        .join(Subject, ProfileSubject.subject_id == Subject.subject_id)
        .filter(ProfileSubject.profile_id == profile.profile_id)
        .order_by(ProfileSubject.slot_position)
        .all()
    )

    fields = (
        db.query(ProfileInterest, FieldOfInterest)
        .join(FieldOfInterest, ProfileInterest.field_id == FieldOfInterest.field_id)
        .filter(ProfileInterest.profile_id == profile.profile_id)
        .all()
    )

    district = (
        db.query(District)
        .filter(District.district_id == profile.district_id)
        .first()
    )

    stream = (
        db.query(ALevelStream)
        .filter(ALevelStream.stream_id == profile.stream_id)
        .first()
    )

    recommendation_count = (
        db.query(RecommendationResult)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .count()
    )

    return {
        "profile_id": str(profile.profile_id),
        "user_id": str(profile.user_id),
        "stream": {
            "stream_id": stream.stream_id if stream else profile.stream_id,
            "stream_name": stream.stream_name if stream else None,
        },
        "district": {
            "district_id": district.district_id if district else profile.district_id,
            "district_name": district.district_name if district else None,
            "province": district.province if district else None,
        },
        "z_score": float(profile.z_score),
        "subjects": [
            {
                "subject_id": subject.subject_id,
                "subject_name": subject.subject_name,
                "slot_position": profile_subject.slot_position,
            }
            for profile_subject, subject in subjects
        ],
        "fields_of_interest": [
            {
                "field_id": field.field_id,
                "field_name": field.field_name,
                "category": field.category,
            }
            for profile_interest, field in fields
        ],
        "recommendation_count": recommendation_count,
        "created_at": profile.created_at,
    }


@router.get("/streams")
def get_streams(db: Session = Depends(get_db)):
    streams = db.query(ALevelStream).order_by(ALevelStream.stream_id).all()

    return [
        {
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "description": stream.description,
        }
        for stream in streams
    ]


@router.get("/streams/{stream_id}/subjects")
def get_subjects_by_stream(
    stream_id: int,
    db: Session = Depends(get_db),
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
            "subject_name": subject.subject_name,
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
            "province": district.province,
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
            "category": field.category,
        }
        for field in fields
    ]


@router.post("/", response_model=AcademicProfileCreateResponse)
def create_academic_profile(
    payload: AcademicProfileCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(set(payload.subject_ids)) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subjects must be three different subjects",
        )

    subjects = (
        db.query(Subject)
        .filter(Subject.subject_id.in_(payload.subject_ids))
        .all()
    )

    if len(subjects) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more subjects are invalid",
        )

    for subject in subjects:
        if subject.stream_id != payload.stream_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected subjects must belong to the selected stream",
            )

    district = (
        db.query(District)
        .filter(District.district_id == payload.district_id)
        .first()
    )

    if not district:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid district",
        )

    stream = (
        db.query(ALevelStream)
        .filter(ALevelStream.stream_id == payload.stream_id)
        .first()
    )

    if not stream:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid A/L stream",
        )

    if payload.field_ids:
        valid_field_count = (
            db.query(FieldOfInterest)
            .filter(FieldOfInterest.field_id.in_(payload.field_ids))
            .count()
        )

        if valid_field_count != len(set(payload.field_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more fields of interest are invalid",
            )

    profile = AcademicProfile(
        user_id=current_user.user_id,
        stream_id=payload.stream_id,
        district_id=payload.district_id,
        z_score=payload.z_score,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    for index, subject_id in enumerate(payload.subject_ids, start=1):
        db.add(
            ProfileSubject(
                profile_id=profile.profile_id,
                subject_id=subject_id,
                slot_position=index,
            )
        )

    for field_id in payload.field_ids:
        db.add(
            ProfileInterest(
                profile_id=profile.profile_id,
                field_id=field_id,
            )
        )

    db.commit()

    log_student_activity(
        db=db,
        user_id=current_user.user_id,
        action="ACADEMIC_PROFILE_CREATED",
        details={
            "name": current_user.name,
            "email": current_user.email,
            "profile_id": str(profile.profile_id),
            "stream_id": profile.stream_id,
            "stream_name": stream.stream_name,
            "district_id": profile.district_id,
            "district_name": district.district_name,
            "z_score": float(profile.z_score),
            "subject_ids": payload.subject_ids,
            "field_ids": payload.field_ids,
        },
    )

    return {
        "profile_id": str(profile.profile_id),
        "user_id": str(current_user.user_id),
        "stream_id": profile.stream_id,
        "district_id": profile.district_id,
        "z_score": float(profile.z_score),
        "subject_ids": payload.subject_ids,
        "field_ids": payload.field_ids,
        "message": "Academic profile created successfully",
    }


@router.get("/my-profiles")
def get_my_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profiles = (
        db.query(AcademicProfile)
        .filter(AcademicProfile.user_id == current_user.user_id)
        .order_by(AcademicProfile.created_at.desc())
        .all()
    )

    return {
        "user": {
            "user_id": str(current_user.user_id),
            "name": current_user.name,
            "email": current_user.email,
        },
        "total_profiles": len(profiles),
        "profiles": [
            build_profile_response(db, profile)
            for profile in profiles
        ],
    }


@router.get("/my-profiles/{profile_id}")
def get_my_profile_by_id(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(AcademicProfile)
        .filter(AcademicProfile.profile_id == profile_id)
        .filter(AcademicProfile.user_id == current_user.user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic profile not found",
        )

    return build_profile_response(db, profile)


@router.delete("/my-profiles/{profile_id}")
def delete_my_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(AcademicProfile)
        .filter(AcademicProfile.profile_id == profile_id)
        .filter(AcademicProfile.user_id == current_user.user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic profile not found",
        )

    deleted_profile_id = str(profile.profile_id)

    db.query(RecommendationResult).filter(
        RecommendationResult.profile_id == profile.profile_id
    ).delete()

    db.query(ProfileInterest).filter(
        ProfileInterest.profile_id == profile.profile_id
    ).delete()

    db.query(ProfileSubject).filter(
        ProfileSubject.profile_id == profile.profile_id
    ).delete()

    db.delete(profile)
    db.commit()

    log_student_activity(
        db=db,
        user_id=current_user.user_id,
        action="ACADEMIC_PROFILE_DELETED",
        details={
            "name": current_user.name,
            "email": current_user.email,
            "profile_id": deleted_profile_id,
        },
    )

    return {
        "message": "Academic profile deleted successfully",
        "profile_id": deleted_profile_id,
    }