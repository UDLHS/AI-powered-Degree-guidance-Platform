from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendationRequest(BaseModel):
    stream_id: int
    subject_ids: List[int] = Field(min_length=3, max_length=3)
    district_id: int
    z_score: float
    field_ids: Optional[List[int]] = []


class RecommendationItem(BaseModel):
    program_id: int
    program_name: str
    university_id: int
    duration_years: int
    job_demand_score: int | None
    cutoff_mark: float
    user_z_score: float
    margin: float
    match_type: str


class RecommendationResponse(BaseModel):
    best_matching: List[RecommendationItem]
    pending_borderline: List[RecommendationItem]