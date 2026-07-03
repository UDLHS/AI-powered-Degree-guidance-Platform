from app.database import SessionLocal
from app.models.academic import ALevelStream, Subject, District, FieldOfInterest
from app.models.university import (
    University,
    DegreeProgram,
    CutoffMark,
    ProgramCareer,
    ProgramCourse,
    Specialization
)
from app.models.admin import Admin
from app.utils.security import hash_password
from app.models.university import ProgramField

def seed_streams(db):
    streams = [
        (1, "Physical Science", "Mathematics stream"),
        (2, "Biology", "Biological science stream"),
        (3, "Technology", "Technology stream"),
        (4, "Commerce", "Commerce stream"),
        (5, "Arts", "Arts stream"),
        (6, "Common", "Common degree entry stream"),
    ]

    for stream_id, stream_name, description in streams:
        exists = db.query(ALevelStream).filter_by(stream_id=stream_id).first()
        if not exists:
            db.add(
                ALevelStream(
                    stream_id=stream_id,
                    stream_name=stream_name,
                    description=description
                )
            )


def seed_subjects(db):
    subjects = [
        # Physical Science
        (1, 1, "Combined Mathematics"),
        (2, 1, "Physics"),
        (3, 1, "Chemistry"),
        (4, 1, "Information and Communication Technology"),

        # Biology
        (5, 2, "Biology"),
        (6, 2, "Physics"),
        (7, 2, "Chemistry"),
        (8, 2, "Agricultural Science"),

        # Technology
        (9, 3, "Engineering Technology"),
        (10, 3, "Bio Systems Technology"),
        (11, 3, "Science for Technology"),
        (12, 3, "Information and Communication Technology"),

        # Commerce
        (13, 4, "Accounting"),
        (14, 4, "Business Studies"),
        (15, 4, "Economics"),
        (16, 4, "Business Statistics"),

        # Arts
        (17, 5, "Political Science"),
        (18, 5, "Geography"),
        (19, 5, "History"),
        (20, 5, "Sinhala"),
        (21, 5, "English"),
        (22, 5, "Logic and Scientific Method"),

        # Common
        (23, 6, "General English"),
        (24, 6, "General Knowledge"),
    ]

    for subject_id, stream_id, subject_name in subjects:
        exists = db.query(Subject).filter_by(subject_id=subject_id).first()
        if not exists:
            db.add(
                Subject(
                    subject_id=subject_id,
                    stream_id=stream_id,
                    subject_name=subject_name
                )
            )


def seed_districts(db):
    districts = [
        (1, "Ampara", "Eastern"),
        (2, "Anuradhapura", "North Central"),
        (3, "Badulla", "Uva"),
        (4, "Batticaloa", "Eastern"),
        (5, "Colombo", "Western"),
        (6, "Galle", "Southern"),
        (7, "Gampaha", "Western"),
        (8, "Hambantota", "Southern"),
        (9, "Jaffna", "Northern"),
        (10, "Kalutara", "Western"),
        (11, "Kandy", "Central"),
        (12, "Kegalle", "Sabaragamuwa"),
        (13, "Kilinochchi", "Northern"),
        (14, "Kurunegala", "North Western"),
        (15, "Mannar", "Northern"),
        (16, "Matale", "Central"),
        (17, "Matara", "Southern"),
        (18, "Monaragala", "Uva"),
        (19, "Mullaitivu", "Northern"),
        (20, "Nuwara Eliya", "Central"),
        (21, "Polonnaruwa", "North Central"),
        (22, "Puttalam", "North Western"),
        (23, "Ratnapura", "Sabaragamuwa"),
        (24, "Trincomalee", "Eastern"),
        (25, "Vavuniya", "Northern"),
    ]

    for district_id, district_name, province in districts:
        exists = db.query(District).filter_by(district_id=district_id).first()
        if not exists:
            db.add(
                District(
                    district_id=district_id,
                    district_name=district_name,
                    province=province
                )
            )


def seed_fields_of_interest(db):
    fields = [
        (1, "Software Engineering", "Technology"),
        (2, "Data Science", "Technology"),
        (3, "Artificial Intelligence", "Technology"),
        (4, "Cyber Security", "Technology"),
        (5, "Engineering", "Engineering"),
        (6, "Medicine", "Health Science"),
        (7, "Biotechnology", "Science"),
        (8, "Agriculture", "Science"),
        (9, "Finance", "Business"),
        (10, "Accounting", "Business"),
        (11, "Marketing", "Business"),
        (12, "Management", "Business"),
        (13, "Law", "Social Science"),
        (14, "Education", "Education"),
        (15, "Creative Arts", "Arts"),
        (16, "Media and Communication", "Arts"),
    ]

    for field_id, field_name, category in fields:
        exists = db.query(FieldOfInterest).filter_by(field_id=field_id).first()
        if not exists:
            db.add(
                FieldOfInterest(
                    field_id=field_id,
                    field_name=field_name,
                    category=category
                )
            )


def seed_universities(db):
    universities = [
        (
            1,
            "University of Colombo",
            "Colombo",
            "https://cmb.ac.lk",
            None,
            "https://www.ugc.ac.lk",
            "One of the leading state universities in Sri Lanka."
        ),
        (
            2,
            "University of Moratuwa",
            "Moratuwa",
            "https://uom.lk",
            None,
            "https://www.ugc.ac.lk",
            "A leading university for engineering, technology, and IT-related degrees."
        ),
        (
            3,
            "University of Kelaniya",
            "Kelaniya",
            "https://kln.ac.lk",
            None,
            "https://www.ugc.ac.lk",
            "A major state university offering science, commerce, arts, and computing degrees."
        ),
    ]

    for university_id, name, location, website_url, logo_image_path, ugc_url, description in universities:
        exists = db.query(University).filter_by(university_id=university_id).first()

        if not exists:
            db.add(
                University(
                    university_id=university_id,
                    name=name,
                    location=location,
                    website_url=website_url,
                    logo_image_path=logo_image_path,
                    ugc_url=ugc_url,
                    description=description
                )
            )


def seed_degree_programs(db):
    programs = [
        (
            1,
            1,
            1,
            "BSc in Computer Science",
            4,
            "Programming, algorithms, databases, AI, software engineering, and research project.",
            10,
            "https://www.ugc.ac.lk"
        ),
        (
            2,
            2,
            1,
            "BSc Engineering",
            4,
            "Engineering mathematics, mechanics, electronics, civil, mechanical, and computer engineering foundations.",
            9,
            "https://www.ugc.ac.lk"
        ),
        (
            3,
            3,
            1,
            "BSc in Physical Science",
            3,
            "Mathematics, physics, chemistry, statistics, and computing fundamentals.",
            7,
            "https://www.ugc.ac.lk"
        ),
        (
            4,
            3,
            4,
            "Bachelor of Commerce",
            4,
            "Accounting, finance, economics, management, and business analytics.",
            8,
            "https://www.ugc.ac.lk"
        ),
        (
            5,
            1,
            2,
            "BSc in Biological Science",
            3,
            "Biology, chemistry, molecular science, environmental science, and laboratory practicals.",
            7,
            "https://www.ugc.ac.lk"
        ),
    ]

    for program_id, university_id, stream_id, program_name, duration_years, syllabus_summary, job_demand_score, ugc_link in programs:
        exists = db.query(DegreeProgram).filter_by(program_id=program_id).first()

        if not exists:
            db.add(
                DegreeProgram(
                    program_id=program_id,
                    university_id=university_id,
                    stream_id=stream_id,
                    program_name=program_name,
                    duration_years=duration_years,
                    syllabus_summary=syllabus_summary,
                    job_demand_score=job_demand_score,
                    ugc_link=ugc_link
                )
            )


def seed_cutoff_marks(db):
    cutoffs = [
        # Colombo district = district_id 5
        # Physical Science stream programs
        (1, 1, 5, 2024, 1.6500),
        (2, 2, 5, 2024, 1.9000),
        (3, 3, 5, 2024, 1.4500),

        # Other districts for testing
        (4, 1, 7, 2024, 1.6000),   # Gampaha
        (5, 2, 7, 2024, 1.8500),
        (6, 3, 7, 2024, 1.3500),

        # Commerce
        (7, 4, 5, 2024, 1.3000),

        # Biology
        (8, 5, 5, 2024, 1.5000),
    ]

    for cutoff_id, program_id, district_id, year, min_cutoff_mark in cutoffs:
        exists = db.query(CutoffMark).filter_by(cutoff_id=cutoff_id).first()

        if not exists:
            db.add(
                CutoffMark(
                    cutoff_id=cutoff_id,
                    program_id=program_id,
                    district_id=district_id,
                    year=year,
                    min_cutoff_mark=min_cutoff_mark
                )
            )


def seed_program_details(db):
    careers = [
        (1, 1, "Software Engineer", "Technology", "Develops software systems and applications."),
        (2, 1, "Data Scientist", "Technology", "Analyzes data and builds predictive models."),
        (3, 2, "Engineer", "Engineering", "Works in engineering design, construction, and technical industries."),
        (4, 3, "Research Assistant", "Science", "Supports scientific research and laboratory work."),
        (5, 4, "Financial Analyst", "Business", "Analyzes financial and business performance."),
        (6, 5, "Laboratory Scientist", "Science", "Works in biological and laboratory-based industries."),
    ]

    for career_id, program_id, role_title, industry, description in careers:
        exists = db.query(ProgramCareer).filter_by(career_id=career_id).first()

        if not exists:
            db.add(
                ProgramCareer(
                    career_id=career_id,
                    program_id=program_id,
                    role_title=role_title,
                    industry=industry,
                    description=description
                )
            )

    courses = [
        (1, 1, "Programming Fundamentals", 1, True),
        (2, 1, "Database Systems", 2, True),
        (3, 1, "Artificial Intelligence", 3, True),
        (4, 2, "Engineering Mathematics", 1, True),
        (5, 2, "Mechanics", 1, True),
        (6, 3, "Physics", 1, True),
        (7, 4, "Financial Accounting", 1, True),
        (8, 5, "Molecular Biology", 2, True),
    ]

    for course_id, program_id, course_name, year_level, is_core in courses:
        exists = db.query(ProgramCourse).filter_by(course_id=course_id).first()

        if not exists:
            db.add(
                ProgramCourse(
                    course_id=course_id,
                    program_id=program_id,
                    course_name=course_name,
                    year_level=year_level,
                    is_core=is_core
                )
            )

    specializations = [
        (1, 1, "Artificial Intelligence", "AI, machine learning, and intelligent systems."),
        (2, 1, "Software Engineering", "Software development, testing, and project management."),
        (3, 2, "Computer Engineering", "Computer systems and embedded engineering."),
        (4, 4, "Finance", "Corporate finance and investment analysis."),
        (5, 5, "Biotechnology", "Biological technology and lab-based innovation."),
    ]

    for spec_id, program_id, spec_name, description in specializations:
        exists = db.query(Specialization).filter_by(spec_id=spec_id).first()

        if not exists:
            db.add(
                Specialization(
                    spec_id=spec_id,
                    program_id=program_id,
                    spec_name=spec_name,
                    description=description
                )
            )

def seed_admin(db):
    admin_email = "admin@aidg.lk"

    exists = db.query(Admin).filter(Admin.email == admin_email).first()

    if not exists:
        db.add(
            Admin(
                name="System Admin",
                email=admin_email,
                password_hash=hash_password("Admin12345"),
                is_active=True
            )
        )


def seed_program_fields(db):
    program_fields = [
        # BSc Computer Science
        (1, 1),  # Software Engineering
        (1, 2),  # Data Science
        (1, 3),  # Artificial Intelligence
        (1, 4),  # Cyber Security

        # BSc Engineering
        (2, 5),  # Engineering
        (2, 1),  # Software Engineering

        # BSc Physical Science
        (3, 2),  # Data Science
        (3, 5),  # Engineering

        # Bachelor of Commerce
        (4, 9),   # Finance
        (4, 10),  # Accounting
        (4, 12),  # Management

        # Biological Science
        (5, 6),  # Medicine / Health Science
        (5, 7),  # Biotechnology
        (5, 8),  # Agriculture
    ]

    for program_id, field_id in program_fields:
        exists = (
            db.query(ProgramField)
            .filter(ProgramField.program_id == program_id)
            .filter(ProgramField.field_id == field_id)
            .first()
        )

        if not exists:
            db.add(
                ProgramField(
                    program_id=program_id,
                    field_id=field_id
                )
            )

def main():
    db = SessionLocal()

    try:
        # Basic lookup data
        seed_streams(db)
        seed_subjects(db)
        seed_districts(db)
        seed_fields_of_interest(db)
        db.flush()

        seed_universities(db)
        db.flush()

        seed_degree_programs(db)
        db.flush()


        seed_cutoff_marks(db)
        db.flush()

        seed_program_details(db)
        db.flush()

        seed_admin(db)
        db.flush()

        seed_program_fields(db)
        db.flush()

        db.commit()
        print("Seed data inserted successfully.")

    except Exception as error:
        db.rollback()
        print("Seed data failed.")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    main()