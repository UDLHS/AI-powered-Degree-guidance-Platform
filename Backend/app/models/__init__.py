
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
)
from app.models.admin import (
    Admin,
    AdminAuditLog,
    UploadedPDF,
    OCRJob,
    OCRExtractedRow,
)