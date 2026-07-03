from pydantic import BaseModel, Field
from typing import List


class AcademicProfileCreateRequest(BaseModel):
    stream_id: int
    district_id: int
    z_score: float = Field(ge=-5.0000, le=5.0000)
    subject_ids: List[int] = Field(min_length=3, max_length=3)
    field_ids: List[int] = []


class AcademicProfileCreateResponse(BaseModel):
    profile_id: str
    user_id: str
    stream_id: int
    district_id: int
    z_score: float
    subject_ids: List[int]
    field_ids: List[int]
    message: str