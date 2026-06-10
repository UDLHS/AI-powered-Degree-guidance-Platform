import uuid
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ALevelStream(Base):
    __tablename__ = "a_level_streams"

    stream_id = Column(Integer, primary_key=True, index=True)
    stream_name = Column(String(80), nullable=False, unique=True)
    description = Column(String, nullable=True)

    subjects = relationship("Subject", back_populates="stream")
    degree_programs = relationship("DegreeProgram", back_populates="stream")


class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("a_level_streams.stream_id"), nullable=False)
    subject_name = Column(String(120), nullable=False)

    stream = relationship("ALevelStream", back_populates="subjects")


class District(Base):
    __tablename__ = "districts"

    district_id = Column(Integer, primary_key=True, index=True)
    district_name = Column(String(80), nullable=False, unique=True)
    province = Column(String(80), nullable=False)


class FieldOfInterest(Base):
    __tablename__ = "fields_of_interest"

    field_id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(100), nullable=False, unique=True)
    category = Column(String(80), nullable=True)


class AcademicProfile(Base):
    __tablename__ = "academic_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    stream_id = Column(Integer, ForeignKey("a_level_streams.stream_id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id"), nullable=False)
    z_score = Column(Numeric(7, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="academic_profiles")
    profile_subjects = relationship("ProfileSubject", back_populates="profile")
    profile_interests = relationship("ProfileInterest", back_populates="profile")
    recommendation_results = relationship("RecommendationResult", back_populates="profile")


class ProfileSubject(Base):
    __tablename__ = "profile_subjects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("academic_profiles.profile_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    slot_position = Column(SmallInteger, nullable=False)

    profile = relationship("AcademicProfile", back_populates="profile_subjects")


class ProfileInterest(Base):
    __tablename__ = "profile_interests"

    profile_id = Column(UUID(as_uuid=True), ForeignKey("academic_profiles.profile_id"), primary_key=True)
    field_id = Column(Integer, ForeignKey("fields_of_interest.field_id"), primary_key=True)

    profile = relationship("AcademicProfile", back_populates="profile_interests")

class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("academic_profiles.profile_id"), nullable=False)
    program_id = Column(Integer, ForeignKey("degree_programs.program_id"), nullable=False)
    match_type = Column(String(10), nullable=False)  # BEST / PENDING
    margin = Column(Numeric(6, 4), nullable=False)
    rank = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("AcademicProfile", back_populates="recommendation_results")
    degree_program = relationship("DegreeProgram")