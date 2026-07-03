from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.utils.security import verify_password, create_access_token

from app.database import get_db
from app.schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse
)
from app.services.auth_service import register_user, login_user


router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    return register_user(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(db, payload)


@router.post("/token")
def login_for_swagger_authorize(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }