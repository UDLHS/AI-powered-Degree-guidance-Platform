from sqlalchemy.orm import Session
from app.models.user import StudentActivityLog


def log_student_activity(
    db: Session,
    user_id=None,
    action: str = "",
    details: dict | None = None
):
    activity = StudentActivityLog(
        user_id=user_id,
        action=action,
        details=details or {}
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity