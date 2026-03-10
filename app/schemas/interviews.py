import re
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


_LIST_SPLIT_PATTERN = re.compile(r"[,\n，；;、]+")


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in _LIST_SPLIT_PATTERN.split(value) if item.strip()]
    if isinstance(value, list):
        normalized: list[str] = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                normalized.append(text)
        return normalized
    return []


class CandidateProfileBase(BaseModel):
    user_id: int = Field(description="关联用户ID")
    avatar: Optional[str] = None
    headline: Optional[str] = None
    resume_text: Optional[str] = None
    skill_tags: list[str] = Field(default_factory=list)
    work_years: int = 0
    education: Optional[str] = None
    target_position: Optional[str] = None
    target_city: Optional[str] = None
    job_status: str = "open"
    strengths: Optional[str] = None
    is_active: bool = True

    @field_validator("skill_tags", mode="before")
    @classmethod
    def validate_skill_tags(cls, value: Any) -> list[str]:
        return _normalize_string_list(value)


class CandidateCreate(CandidateProfileBase):
    pass


class CandidateUpdate(CandidateProfileBase):
    id: int


class CandidateSelfUpsert(BaseModel):
    avatar: Optional[str] = None
    headline: Optional[str] = None
    resume_text: Optional[str] = None
    skill_tags: list[str] = Field(default_factory=list)
    work_years: int = 0
    education: Optional[str] = None
    target_position: Optional[str] = None
    target_city: Optional[str] = None
    job_status: str = "open"
    strengths: Optional[str] = None
    is_active: bool = True

    @field_validator("skill_tags", mode="before")
    @classmethod
    def validate_skill_tags(cls, value: Any) -> list[str]:
        return _normalize_string_list(value)


class InterviewPositionBase(BaseModel):
    title: str
    category: Optional[str] = None
    level: Optional[str] = None
    department: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    difficulty: str = "middle"
    cover_image: Optional[str] = None
    summary: Optional[str] = None
    highlight: list[str] = Field(default_factory=list)
    is_recommended: bool = True
    status: str = "online"

    @field_validator("tags", "highlight", mode="before")
    @classmethod
    def validate_tag_fields(cls, value: Any) -> list[str]:
        return _normalize_string_list(value)


class InterviewPositionCreate(InterviewPositionBase):
    pass


class InterviewPositionUpdate(InterviewPositionBase):
    id: int


class PositionJDBase(BaseModel):
    position_id: int
    version: int = 1
    jd_text: str
    must_have_tags: list[str] = Field(default_factory=list)
    bonus_tags: list[str] = Field(default_factory=list)
    scoring_dimensions: list[str] = Field(default_factory=list)
    prompt_hint: Optional[str] = None
    is_active: bool = True

    @field_validator("must_have_tags", "bonus_tags", "scoring_dimensions", mode="before")
    @classmethod
    def validate_list_fields(cls, value: Any) -> list[str]:
        return _normalize_string_list(value)


class PositionJDCreate(PositionJDBase):
    pass


class PositionJDUpdate(PositionJDBase):
    id: int


class InterviewSessionCreate(BaseModel):
    candidate_id: int
    position_id: int
    jd_id: Optional[int] = None
    status: str = "pending"
    total_rounds: int = 5
    question_plan: list[dict[str, Any]] = Field(default_factory=list)
    context_summary: Optional[str] = None
    ai_persona: dict[str, Any] = Field(default_factory=dict)
    latest_metrics: dict[str, Any] = Field(default_factory=dict)
    session_no: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    @field_validator("question_plan", mode="before")
    @classmethod
    def validate_question_plan(cls, value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return []


class InterviewSessionUpdate(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    position_id: Optional[int] = None
    jd_id: Optional[int] = None
    status: Optional[str] = None
    current_round: Optional[int] = None
    total_rounds: Optional[int] = None
    question_plan: Optional[list[dict[str, Any]]] = None
    context_summary: Optional[str] = None
    ai_persona: Optional[dict[str, Any]] = None
    latest_metrics: Optional[dict[str, Any]] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    @field_validator("question_plan", mode="before")
    @classmethod
    def validate_question_plan(cls, value: Any) -> Optional[list[dict[str, Any]]]:
        if value is None:
            return None
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return None


class InterviewReportBase(BaseModel):
    session_id: int
    candidate_id: int
    position_id: int
    total_score: int = 0
    dimension_scores: dict[str, Any] = Field(default_factory=dict)
    overview: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    recommended_positions: list[str] = Field(default_factory=list)
    archive_status: str = "archived"
    pdf_url: Optional[str] = None
    report_payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("highlights", "risks", "suggestions", "recommended_positions", mode="before")
    @classmethod
    def validate_text_lists(cls, value: Any) -> list[str]:
        return _normalize_string_list(value)


class InterviewReportCreate(InterviewReportBase):
    pass


class InterviewReportUpdate(BaseModel):
    id: int
    total_score: Optional[int] = None
    dimension_scores: Optional[dict[str, Any]] = None
    overview: Optional[str] = None
    highlights: Optional[list[str]] = None
    risks: Optional[list[str]] = None
    suggestions: Optional[list[str]] = None
    recommended_positions: Optional[list[str]] = None
    archive_status: Optional[str] = None
    pdf_url: Optional[str] = None
    report_payload: Optional[dict[str, Any]] = None

    @field_validator("highlights", "risks", "suggestions", "recommended_positions", mode="before")
    @classmethod
    def validate_text_lists(cls, value: Any) -> Optional[list[str]]:
        if value is None:
            return None
        return _normalize_string_list(value)


class StartMockInterviewIn(BaseModel):
    position_id: int
    total_rounds: int = Field(default=5, ge=3, le=8)


class SubmitInterviewSegmentIn(BaseModel):
    session_id: int
    content: str = Field(min_length=1, max_length=3000)
    segment_index: int = 1


class NextInterviewQuestionIn(BaseModel):
    session_id: int


class FinishMockInterviewIn(BaseModel):
    session_id: int


class CandidateDashboardOut(BaseModel):
    profile_ready: bool
    readiness_score: int
    interview_count: int
    report_count: int
    average_score: int
    latest_report: Optional[dict[str, Any]] = None
    featured_positions: list[dict[str, Any]] = Field(default_factory=list)


DEFAULT_SCORING_DIMENSIONS = ["专业能力", "表达沟通", "岗位匹配", "稳定度"]
