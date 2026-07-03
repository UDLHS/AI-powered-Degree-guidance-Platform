from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendation_schema import RecommendationRequest
from app.services.recommendation_service import get_recommendations
from app.services.activity_service import log_student_activity
from app.models.user import User
from app.models.academic import (
    AcademicProfile,
    ProfileSubject,
    ProfileInterest,
    RecommendationResult,
    ALevelStream,
    District,
)
from app.models.university import DegreeProgram, University, CutoffMark
from app.utils.security import get_current_user


router = APIRouter()


def get_user_profile_or_404(
    db: Session,
    profile_id: UUID,
    current_user: User
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
            detail="Academic profile not found"
        )

    return profile


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
        field_ids=payload.field_ids,
        min_job_demand_score=payload.min_job_demand_score,
        max_pending_margin=payload.max_pending_margin,
        result_type=payload.result_type
    )


@router.post("/from-profile/{profile_id}")
def recommend_from_saved_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_user_profile_or_404(db, profile_id, current_user)

    interest_rows = (
        db.query(ProfileInterest)
        .filter(ProfileInterest.profile_id == profile.profile_id)
        .all()
    )

    field_ids = [row.field_id for row in interest_rows]

    recommendations = get_recommendations(
        db=db,
        stream_id=profile.stream_id,
        district_id=profile.district_id,
        z_score=float(profile.z_score),
        field_ids=field_ids,
        profile_id=profile.profile_id,
        save_results=True
    )

    total_results = (
        db.query(RecommendationResult)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .count()
    )

    best_count = (
        db.query(RecommendationResult)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .filter(RecommendationResult.match_type == "BEST")
        .count()
    )

    pending_count = (
        db.query(RecommendationResult)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .filter(RecommendationResult.match_type == "PENDING")
        .count()
    )

    log_student_activity(
        db=db,
        user_id=current_user.user_id,
        action="RECOMMENDATION_GENERATED",
        details={
            "name": current_user.name,
            "email": current_user.email,
            "profile_id": str(profile.profile_id),
            "stream_id": profile.stream_id,
            "district_id": profile.district_id,
            "z_score": float(profile.z_score),
            "field_ids": field_ids,
            "total_results": total_results,
            "best_count": best_count,
            "pending_count": pending_count,
        }
    )

    return recommendations


@router.get("/history/{profile_id}")
def get_recommendation_history(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_user_profile_or_404(db, profile_id, current_user)

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


@router.get("/my-results")
def get_my_recommendation_result_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profiles = (
        db.query(AcademicProfile, ALevelStream, District)
        .join(ALevelStream, AcademicProfile.stream_id == ALevelStream.stream_id)
        .join(District, AcademicProfile.district_id == District.district_id)
        .filter(AcademicProfile.user_id == current_user.user_id)
        .order_by(AcademicProfile.created_at.desc())
        .all()
    )

    result = []

    for profile, stream, district in profiles:
        total_results = (
            db.query(RecommendationResult)
            .filter(RecommendationResult.profile_id == profile.profile_id)
            .count()
        )

        best_count = (
            db.query(RecommendationResult)
            .filter(RecommendationResult.profile_id == profile.profile_id)
            .filter(RecommendationResult.match_type == "BEST")
            .count()
        )

        pending_count = (
            db.query(RecommendationResult)
            .filter(RecommendationResult.profile_id == profile.profile_id)
            .filter(RecommendationResult.match_type == "PENDING")
            .count()
        )

        result.append({
            "profile_id": str(profile.profile_id),
            "stream_name": stream.stream_name,
            "district_name": district.district_name,
            "z_score": float(profile.z_score),
            "total_results": total_results,
            "best_count": best_count,
            "pending_count": pending_count,
            "created_at": profile.created_at
        })

    return {
        "user": {
            "user_id": str(current_user.user_id),
            "name": current_user.name,
            "email": current_user.email
        },
        "total_profiles": len(result),
        "profiles": result
    }


@router.get("/my-results/{profile_id}")
def get_my_recommendation_results_by_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_user_profile_or_404(db, profile_id, current_user)

    rows = (
        db.query(RecommendationResult, DegreeProgram, University)
        .join(DegreeProgram, RecommendationResult.program_id == DegreeProgram.program_id)
        .join(University, DegreeProgram.university_id == University.university_id)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .order_by(RecommendationResult.match_type, RecommendationResult.rank)
        .all()
    )

    best_matching = []
    pending_borderline = []

    for recommendation, program, university in rows:
        latest_cutoff = (
            db.query(CutoffMark)
            .filter(CutoffMark.program_id == program.program_id)
            .filter(CutoffMark.district_id == profile.district_id)
            .order_by(CutoffMark.year.desc())
            .first()
        )

        item = {
            "result_id": str(recommendation.result_id),
            "program_id": program.program_id,
            "program_name": program.program_name,
            "university_id": university.university_id,
            "university_name": university.name,
            "location": university.location,
            "duration_years": program.duration_years,
            "syllabus_summary": program.syllabus_summary,
            "job_demand_score": program.job_demand_score,
            "ugc_link": program.ugc_link,
            "match_type": recommendation.match_type,
            "margin": float(recommendation.margin),
            "rank": recommendation.rank,
            "created_at": recommendation.created_at,
            "latest_cutoff": {
                "year": latest_cutoff.year if latest_cutoff else None,
                "cutoff_mark": float(latest_cutoff.min_cutoff_mark) if latest_cutoff else None
            }
        }

        if recommendation.match_type == "BEST":
            best_matching.append(item)
        else:
            pending_borderline.append(item)

    return {
        "profile": {
            "profile_id": str(profile.profile_id),
            "stream_id": profile.stream_id,
            "district_id": profile.district_id,
            "z_score": float(profile.z_score),
            "created_at": profile.created_at
        },
        "total_results": len(best_matching) + len(pending_borderline),
        "best_matching": best_matching,
        "pending_borderline": pending_borderline
    }


@router.delete("/my-results/{profile_id}")
def delete_my_recommendation_results(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_user_profile_or_404(db, profile_id, current_user)

    deleted_count = (
        db.query(RecommendationResult)
        .filter(RecommendationResult.profile_id == profile.profile_id)
        .delete()
    )

    db.commit()

    log_student_activity(
        db=db,
        user_id=current_user.user_id,
        action="RECOMMENDATION_RESULTS_DELETED",
        details={
            "name": current_user.name,
            "email": current_user.email,
            "profile_id": str(profile.profile_id),
            "deleted_count": deleted_count,
        }
    )

    return {
        "message": "Recommendation results deleted successfully",
        "profile_id": str(profile.profile_id),
        "deleted_count": deleted_count
    }