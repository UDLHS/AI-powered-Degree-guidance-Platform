from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.university import (
    University,
    DegreeProgram,
    CutoffMark,
    ProgramCareer,
    ProgramCourse,
    Specialization
)


router = APIRouter()


@router.get("/")
def get_all_universities(db: Session = Depends(get_db)):
    universities = db.query(University).order_by(University.name).all()

    return [
        {
            "university_id": university.university_id,
            "name": university.name,
            "location": university.location,
            "website_url": university.website_url,
            "logo_image_path": university.logo_image_path,
            "ugc_url": university.ugc_url,
            "description": university.description
        }
        for university in universities
    ]


@router.get("/{university_id}")
def get_university_by_id(
    university_id: int,
    db: Session = Depends(get_db)
):
    university = (
        db.query(University)
        .filter(University.university_id == university_id)
        .first()
    )

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found"
        )

    return {
        "university_id": university.university_id,
        "name": university.name,
        "location": university.location,
        "website_url": university.website_url,
        "logo_image_path": university.logo_image_path,
        "ugc_url": university.ugc_url,
        "description": university.description
    }


@router.get("/{university_id}/programs")
def get_programs_by_university(
    university_id: int,
    db: Session = Depends(get_db)
):
    university = (
        db.query(University)
        .filter(University.university_id == university_id)
        .first()
    )

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found"
        )

    programs = (
        db.query(DegreeProgram)
        .filter(DegreeProgram.university_id == university_id)
        .order_by(DegreeProgram.program_name)
        .all()
    )

    return {
        "university_id": university.university_id,
        "university_name": university.name,
        "programs": [
            {
                "program_id": program.program_id,
                "program_name": program.program_name,
                "stream_id": program.stream_id,
                "duration_years": program.duration_years,
                "job_demand_score": program.job_demand_score,
                "ugc_link": program.ugc_link
            }
            for program in programs
        ]
    }


@router.get("/programs/{program_id}")
def get_program_details(
    program_id: int,
    db: Session = Depends(get_db)
):
    program = (
        db.query(DegreeProgram)
        .filter(DegreeProgram.program_id == program_id)
        .first()
    )

    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Degree program not found"
        )

    university = (
        db.query(University)
        .filter(University.university_id == program.university_id)
        .first()
    )

    cutoff_history = (
        db.query(CutoffMark)
        .filter(CutoffMark.program_id == program_id)
        .order_by(CutoffMark.year.desc())
        .all()
    )

    careers = (
        db.query(ProgramCareer)
        .filter(ProgramCareer.program_id == program_id)
        .all()
    )

    courses = (
        db.query(ProgramCourse)
        .filter(ProgramCourse.program_id == program_id)
        .order_by(ProgramCourse.year_level)
        .all()
    )

    specializations = (
        db.query(Specialization)
        .filter(Specialization.program_id == program_id)
        .all()
    )

    return {
        "program_id": program.program_id,
        "program_name": program.program_name,
        "duration_years": program.duration_years,
        "syllabus_summary": program.syllabus_summary,
        "job_demand_score": program.job_demand_score,
        "ugc_link": program.ugc_link,
        "university": {
            "university_id": university.university_id,
            "name": university.name,
            "location": university.location,
            "website_url": university.website_url,
            "logo_image_path": university.logo_image_path,
            "ugc_url": university.ugc_url
        },
        "cutoff_history": [
            {
                "cutoff_id": cutoff.cutoff_id,
                "district_id": cutoff.district_id,
                "year": cutoff.year,
                "min_cutoff_mark": float(cutoff.min_cutoff_mark)
            }
            for cutoff in cutoff_history
        ],
        "career_blueprints": [
            {
                "career_id": career.career_id,
                "role_title": career.role_title,
                "industry": career.industry,
                "description": career.description
            }
            for career in careers
        ],
        "core_courses": [
            {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "year_level": course.year_level,
                "is_core": course.is_core
            }
            for course in courses
        ],
        "specializations": [
            {
                "spec_id": specialization.spec_id,
                "spec_name": specialization.spec_name,
                "description": specialization.description
            }
            for specialization in specializations
        ]
    }