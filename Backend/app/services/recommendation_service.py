from sqlalchemy.orm import Session

from app.models.university import DegreeProgram, CutoffMark, University, ProgramField
from app.models.academic import RecommendationResult


def get_recommendations(
    db: Session,
    stream_id: int,
    district_id: int,
    z_score: float,
    field_ids: list[int] | None = None,
    profile_id=None,
    save_results: bool = False,
    min_job_demand_score: int | None = None,
    max_pending_margin: float | None = None,
    result_type: str | None = None
):
    query = (
        db.query(DegreeProgram, CutoffMark, University)
        .join(CutoffMark, DegreeProgram.program_id == CutoffMark.program_id)
        .join(University, DegreeProgram.university_id == University.university_id)
        .filter(DegreeProgram.stream_id == stream_id)
        .filter(CutoffMark.district_id == district_id)
    )

    if min_job_demand_score is not None:
        query = query.filter(DegreeProgram.job_demand_score >= min_job_demand_score)

    if field_ids:
        program_ids_for_fields = (
            db.query(ProgramField.program_id)
            .filter(ProgramField.field_id.in_(field_ids))
            .distinct()
            .subquery()
        )

        query = query.filter(DegreeProgram.program_id.in_(program_ids_for_fields))

    rows = query.all()

    best_matches = []
    pending_matches = []

    for program, cutoff, university in rows:
        margin = float(z_score) - float(cutoff.min_cutoff_mark)

        item = {
            "program_id": program.program_id,
            "program_name": program.program_name,
            "university_id": university.university_id,
            "university_name": university.name,
            "location": university.location,
            "duration_years": program.duration_years,
            "syllabus_summary": program.syllabus_summary,
            "job_demand_score": program.job_demand_score,
            "ugc_link": program.ugc_link,
            "cutoff_year": cutoff.year,
            "cutoff_mark": float(cutoff.min_cutoff_mark),
            "user_z_score": float(z_score),
            "margin": round(margin, 4),
        }

        if margin >= 0:
            item["match_type"] = "BEST"
            best_matches.append(item)
        else:
            if max_pending_margin is not None:
                if abs(margin) > max_pending_margin:
                    continue

            item["match_type"] = "PENDING"
            pending_matches.append(item)

    best_matches.sort(
        key=lambda x: (
            x["job_demand_score"] if x["job_demand_score"] is not None else 0,
            x["margin"]
        ),
        reverse=True
    )

    pending_matches.sort(key=lambda x: abs(x["margin"]))

    for index, item in enumerate(best_matches, start=1):
        item["rank"] = index

    for index, item in enumerate(pending_matches, start=1):
        item["rank"] = index

    if save_results and profile_id:
        db.query(RecommendationResult).filter(
            RecommendationResult.profile_id == profile_id
        ).delete()

        for item in best_matches:
            db.add(
                RecommendationResult(
                    profile_id=profile_id,
                    program_id=item["program_id"],
                    match_type="BEST",
                    margin=item["margin"],
                    rank=item["rank"]
                )
            )

        for item in pending_matches:
            db.add(
                RecommendationResult(
                    profile_id=profile_id,
                    program_id=item["program_id"],
                    match_type="PENDING",
                    margin=item["margin"],
                    rank=item["rank"]
                )
            )

        db.commit()

    if result_type == "BEST":
        pending_matches = []

    if result_type == "PENDING":
        best_matches = []

    return {
        "best_matching": best_matches,
        "pending_borderline": pending_matches,
        "filters_applied": {
            "field_ids": field_ids or [],
            "min_job_demand_score": min_job_demand_score,
            "max_pending_margin": max_pending_margin,
            "result_type": result_type or "ALL"
        }
    }