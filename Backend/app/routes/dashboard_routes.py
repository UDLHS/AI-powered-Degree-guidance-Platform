from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.academic import ALevelStream, District, FieldOfInterest
from app.models.university import University, DegreeProgram, CutoffMark


router = APIRouter()


@router.get("/public-summary")
def get_public_dashboard_summary(db: Session = Depends(get_db)):
    total_universities = db.query(University).count()
    total_degree_programs = db.query(DegreeProgram).count()
    total_streams = db.query(ALevelStream).count()
    total_districts = db.query(District).count()
    total_fields_of_interest = db.query(FieldOfInterest).count()

    latest_cutoff_year = db.query(func.max(CutoffMark.year)).scalar()

    programs_by_stream_rows = (
        db.query(
            ALevelStream.stream_id,
            ALevelStream.stream_name,
            func.count(DegreeProgram.program_id).label("program_count")
        )
        .outerjoin(DegreeProgram, DegreeProgram.stream_id == ALevelStream.stream_id)
        .group_by(ALevelStream.stream_id, ALevelStream.stream_name)
        .order_by(ALevelStream.stream_id)
        .all()
    )

    return {
        "summary": {
            "total_universities": total_universities,
            "total_degree_programs": total_degree_programs,
            "total_streams": total_streams,
            "total_districts": total_districts,
            "total_fields_of_interest": total_fields_of_interest,
            "latest_cutoff_year": latest_cutoff_year
        },
        "programs_by_stream": [
            {
                "stream_id": row.stream_id,
                "stream_name": row.stream_name,
                "program_count": row.program_count
            }
            for row in programs_by_stream_rows
        ]
    }


@router.get("/top-programs")
def get_top_programs(db: Session = Depends(get_db)):
    rows = (
        db.query(DegreeProgram, University, ALevelStream)
        .join(University, DegreeProgram.university_id == University.university_id)
        .join(ALevelStream, DegreeProgram.stream_id == ALevelStream.stream_id)
        .order_by(desc(DegreeProgram.job_demand_score))
        .limit(10)
        .all()
    )

    return [
        {
            "program_id": program.program_id,
            "program_name": program.program_name,
            "university_id": university.university_id,
            "university_name": university.name,
            "location": university.location,
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "duration_years": program.duration_years,
            "job_demand_score": program.job_demand_score,
            "ugc_link": program.ugc_link
        }
        for program, university, stream in rows
    ]