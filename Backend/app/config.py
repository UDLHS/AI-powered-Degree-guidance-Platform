from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OCR_POPPLER_PATH: str = ""

    OCR_DPI: int = 400
    OCR_GPU: bool = False
    OCR_POPPLER_PATH: str | None = None
    OCR_OUTPUT_DIR: str = "uploads/ocr_outputs"

    class Config:
        env_file = ".env"


settings = Settings()