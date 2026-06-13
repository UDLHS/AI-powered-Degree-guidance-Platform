from sqlalchemy import Column, Integer, String, Text, SmallInteger, Numeric, Boolean, ForeignKey,Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class University(Base):
    __tablename__ = "universities"

    university_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(120), nullable=False)
    website_url = Column(Text, nullable=True)
    logo_image_path = Column(Text, nullable=True)
    ugc_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    stages = relationship("UniversityStage", back_populates="university")
    degree_programs = relationship("DegreeProgram", back_populates="university")


class UniversityStage(Base):
    __tablename__ = "university_stages"

    stage_id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.university_id"), nullable=False)
    stage_name = Column(String(120), nullable=False)
    location = Column(String(120), nullable=True)

    university = relationship("University", back_populates="stages")


class DegreeProgram(Base):
    __tablename__ = "degree_programs"

    program_id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.university_id"), nullable=False)
    stream_id = Column(Integer, ForeignKey("a_level_streams.stream_id"), nullable=False)
    program_name = Column(String(200), nullable=False)
    duration_years = Column(SmallInteger, nullable=False)
    syllabus_summary = Column(Text, nullable=True)
    job_demand_score = Column(SmallInteger, nullable=True)
    ugc_link = Column(Text, nullable=True)

    university = relationship("University", back_populates="degree_programs")
    stream = relationship("ALevelStream", back_populates="degree_programs")
    cutoff_marks = relationship("CutoffMark", back_populates="degree_program")
    careers = relationship("ProgramCareer", back_populates="degree_program")
    courses = relationship("ProgramCourse", back_populates="degree_program")


class CutoffMark(Base):
    __tablename__ = "cutoff_marks"

    cutoff_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("degree_programs.program_id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.district_id"), nullable=False)
    year = Column(SmallInteger, nullable=False)
    min_cutoff_mark = Column(Numeric(7, 4), nullable=False)
    raw_cutoff_mark = Column(String(50), nullable=True)
    cutoff_status = Column(String(30), nullable=False, default="QUALIFIED")
    is_nqc = Column(Boolean, nullable=False, default=False)

    degree_program = relationship("DegreeProgram", back_populates="cutoff_marks")


class Specialization(Base):
    __tablename__ = "specializations"

    spec_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("degree_programs.program_id"), nullable=False)
    spec_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)


class ProgramCareer(Base):
    __tablename__ = "program_careers"

    career_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("degree_programs.program_id"), nullable=False)
    role_title = Column(String(150), nullable=False)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    degree_program = relationship("DegreeProgram", back_populates="careers")


class ProgramCourse(Base):
    __tablename__ = "program_courses"

    course_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("degree_programs.program_id"), nullable=False)
    course_name = Column(String(200), nullable=False)
    year_level = Column(SmallInteger, nullable=False)
    is_core = Column(Boolean, default=True)

    degree_program = relationship("DegreeProgram", back_populates="courses")

class ProgramField(Base):
    __tablename__ = "program_fields"

    program_id = Column(Integer, ForeignKey("degree_programs.program_id"), primary_key=True)
    field_id = Column(Integer, ForeignKey("fields_of_interest.field_id"), primary_key=True)