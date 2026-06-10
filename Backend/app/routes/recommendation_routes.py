from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendation_schema import RecommendationRequest
from app.services.recommendation_service import get_recommendations
from app.models.academic import AcademicProfile, ProfileSubject, ProfileInterest
from app.models.user import User
from app.utils.security import get_current_user


router = APIRouter()


@router.post("/")
def recommend_courses(
    payload: RecommendationRequest,
    db: Session = Depends(get_db)
):
    return get_recommendations(
        db=db,
        stream_id=payload.stream_id,
        district_id=payload.district_id,
        z_score=payload.z_score,
        field_ids=payload.field_ids
    )


@router.post("/from-profile/{profile_id}")
def recommend_from_saved_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = (
        db.query(AcademicProfile)
        .filter(AcademicProfile.profile_id == profile_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic profile not found"
        )

    if str(profile.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this profile"
        )

    subject_rows = (
        db.query(ProfileSubject)
        .filter(ProfileSubject.profile_id == profile.profile_id)
        .all()
    )

    interest_rows = (
        db.query(ProfileInterest)
        .filter(ProfileInterest.profile_id == profile.profile_id)
        .all()
    )

    subject_ids = [row.subject_id for row in subject_rows]
    field_ids = [row.field_id for row in interest_rows]

    return get_recommendations(
        db=db,
        stream_id=profile.stream_id,
        district_id=profile.district_id,
        z_score=float(profile.z_score),
        field_ids=field_ids,
        profile_id=profile.profile_id,
        save_results=True
    )


@router.get("/history/{profile_id}")
def get_recommendation_history(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = (
        db.query(AcademicProfile)
        .filter(AcademicProfile.profile_id == profile_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic profile not found"
        )

    if str(profile.user_id) != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this profile"
        )

    from app.models.academic import RecommendationResult
    from app.models.university import DegreeProgram, University

    rows = (
        db.query(RecommendationResult, DegreeProgram, University)
        .join(DegreeProgram, RecommendationResult.program_id == DegreeProgram.program_id)
        .join(University, DegreeProgram.university_id == University.university_id)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .order_by(RecommendationResult.match_type, RecommendationResult.rank)
        .all()
    )

    return [
        {
            "result_id": str(result.result_id),
            "program_id": program.program_id,
            "program_name": program.program_name,
            "university_name": university.name,
            "match_type": result.match_type,
            "margin": float(result.margin),
            "rank": result.rank,
            "created_at": result.created_at
        }
        for result, program, university in rows
    ]