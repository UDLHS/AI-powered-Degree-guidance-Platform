from app.database import Base, engine

# Import all models so SQLAlchemy knows every table
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
from app.models.university import (
    University,
    UniversityStage,
    DegreeProgram,
    CutoffMark,
    Specialization,
    ProgramCareer,
    ProgramCourse,
    ProgramField,
)
from app.models.admin import (
    Admin,
    AdminAuditLog,
    UploadedPDF,
    OCRJob,
    OCRExtractedRow,
)


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    print("Created tables:")
    for table_name in Base.metadata.tables.keys():
        print("-", table_name)


if __name__ == "__main__":
    main()