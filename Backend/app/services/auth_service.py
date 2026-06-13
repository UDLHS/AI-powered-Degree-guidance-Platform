from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth_schema import UserRegisterRequest, UserLoginRequest
from app.utils.security import hash_password, verify_password, create_access_token
from app.services.activity_service import log_student_activity


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(db: Session, payload: UserRegisterRequest):
    email = normalize_email(payload.email)

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_student_activity(
        db=db,
        user_id=new_user.user_id,
        action="STUDENT_REGISTERED",
        details={
            "name": new_user.name,
            "email": new_user.email
        }
    )

    access_token = create_access_token(
        data={
            "sub": str(new_user.user_id),
            "email": new_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(new_user.user_id),
        "name": new_user.name,
        "email": new_user.email
    }


def login_user(db: Session, payload: UserLoginRequest):
    email = normalize_email(payload.email)

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    log_student_activity(
        db=db,
        user_id=user.user_id,
        action="STUDENT_LOGGED_IN",
        details={
            "name": user.name,
            "email": user.email
        }
    )

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.user_id),
        "name": user.name,
        "email": user.email
    }