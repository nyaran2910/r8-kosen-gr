from uuid import UUID, uuid4
from decimal import Decimal
from sqlalchemy import (
    CheckConstraint,
    Text,
    ForeignKey,
    Numeric,
    DateTime,
    SmallInteger,
    text,
    Index,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        CheckConstraint("name ~ '[^[:space:]]'", name="ck_subjects_name_not_blank"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)


class Genre(Base):
    __tablename__ = "genres"
    __table_args__ = (
        CheckConstraint("name ~ '[^[:space:]]'", name="ck_genres_name_not_blank"),
        CheckConstraint(
            "description_md ~ '[^[:space:]]'", name="ck_genres_description_not_blank"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description_md: Mapped[str] = mapped_column(Text, nullable=False)


class KnowledgeElement(Base):
    __tablename__ = "knowledge_elements"
    __table_args__ = (
        CheckConstraint("title ~ '[^[:space:]]'", name="ck_knowledge_title_not_blank"),
        CheckConstraint(
            "body_md ~ '[^[:space:]]'",
            name="ck_knowledge_body_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    genre_id: Mapped[UUID] = mapped_column(
        ForeignKey("genres.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)


class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = (
        CheckConstraint("name ~ '[^[:space:]]'", name="ck_exams_name_not_blank"),
        CheckConstraint(
            "category ~ '[^[:space:]]'", name="ck_exams_category_not_blank"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    subject_id: Mapped[UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )


class Format(Base):
    __tablename__ = "formats"
    __table_args__ = (
        CheckConstraint("name ~ '[^[:space:]]'", name="ck_formats_name_not_blank"),
        CheckConstraint(
            "structure ~ '[^[:space:]]'", name="ck_formats_structure_not_blank"
        ),
        CheckConstraint(
            "answer_type ~ '[^[:space:]]'", name="ck_formats_answer_type_not_blank"
        ),
        CheckConstraint(
            "description_md ~ '[^[:space:]]'", name="ck_formats_description_not_blank"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    structure: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[str] = mapped_column(Text, nullable=False)
    description_md: Mapped[str] = mapped_column(Text, nullable=False)


class ExamGenre(Base):
    __tablename__ = "exam_genres"

    exam_id: Mapped[UUID] = mapped_column(
        ForeignKey("exams.id", ondelete="RESTRICT"), primary_key=True
    )
    genre_id: Mapped[UUID] = mapped_column(
        ForeignKey("genres.id", ondelete="RESTRICT"), primary_key=True
    )


class ExamFormat(Base):
    __tablename__ = "exam_formats"

    exam_id: Mapped[UUID] = mapped_column(
        ForeignKey("exams.id", ondelete="RESTRICT"), primary_key=True
    )
    format_id: Mapped[UUID] = mapped_column(
        ForeignKey("formats.id", ondelete="RESTRICT"), primary_key=True
    )


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        CheckConstraint("body_md ~ '[^[:space:]]'", name="ck_problems_body_not_blank"),
        CheckConstraint(
            "answer_md ~ '[^[:space:]]'", name="ck_problems_answer_not_blank"
        ),
        CheckConstraint(
            "explanation_md ~ '[^[:space:]]'", name="ck_problems_explanation_not_blank"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    exam_id: Mapped[UUID] = mapped_column(
        ForeignKey("exams.id", ondelete="RESTRICT"), nullable=False
    )
    format_id: Mapped[UUID] = mapped_column(
        ForeignKey("formats.id", ondelete="RESTRICT"), nullable=False
    )
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    answer_md: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_md: Mapped[str] = mapped_column(Text, nullable=False)
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ProblemGenre(Base):
    __tablename__ = "problem_genres"

    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problems.id", ondelete="RESTRICT"), primary_key=True
    )
    genre_id: Mapped[UUID] = mapped_column(
        ForeignKey("genres.id", ondelete="RESTRICT"), primary_key=True
    )


class ProblemKnowledge(Base):
    __tablename__ = "problem_knowledge"

    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problems.id", ondelete="RESTRICT"), primary_key=True
    )
    knowledge_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_elements.id", ondelete="RESTRICT"), primary_key=True
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "google_sub IS NULL OR google_sub ~ '[^[:space:]]'",
            name="ck_users_google_sub_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    google_sub: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)


class UserKnowledgeState(Base):
    __tablename__ = "user_knowledge_states"
    __table_args__ = (
        CheckConstraint(
            "understanding BETWEEN 1 AND 5",
            name="ck_user_knowledge_understanding_range",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    knowledge_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_elements.id", ondelete="RESTRICT"), primary_key=True
    )
    understanding: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class UserFormatState(Base):
    __tablename__ = "user_format_states"
    __table_args__ = (
        CheckConstraint(
            "understanding BETWEEN 1 AND 5",
            name="ck_user_format_understanding_range",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    exam_id: Mapped[UUID] = mapped_column(
        ForeignKey("exams.id", ondelete="RESTRICT"), primary_key=True
    )
    format_id: Mapped[UUID] = mapped_column(
        ForeignKey("formats.id", ondelete="RESTRICT"), primary_key=True
    )
    understanding: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        CheckConstraint(
            "result IN ('perfect', 'correct', 'incorrect', 'gave_up')",
            name="ck_attempts_result",
        ),
        CheckConstraint(
            "format_understanding_before BETWEEN 1 AND 5",
            name="ck_attempts_format_before",
        ),
        CheckConstraint(
            "format_understanding_after BETWEEN 1 AND 5",
            name="ck_attempts_format_after",
        ),
        CheckConstraint(
            "(submitted_at IS NOT NULL) = (result IS NOT NULL) AND "
            "(submitted_at IS NOT NULL) = (format_understanding_after IS NOT NULL) AND "
            "(submitted_at IS NOT NULL) = (scheduled_review_at IS NOT NULL) AND "
            "(submitted_at IS NOT NULL) = (scheduler_version IS NOT NULL)",
            name="ck_attempts_submission_fields",
        ),
        CheckConstraint(
            "submitted_at IS NOT NULL OR format_understanding_before IS NULL",
            name="ck_attempts_before_requires_submission",
        ),
        CheckConstraint(
            "answer_viewed_at IS NULL OR "
            "(started_at IS NOT NULL AND answer_viewed_at >= started_at)",
            name="ck_attempts_answer_time",
        ),
        CheckConstraint(
            "submitted_at IS NULL OR "
            "(closed_at IS NULL AND answer_viewed_at IS NOT NULL "
            "AND submitted_at >= answer_viewed_at)",
            name="ck_attempts_submission_time",
        ),
        CheckConstraint(
            "scheduler_version IS NULL OR scheduler_version ~ '[^[:space:]]'",
            name="ck_attempts_scheduler_not_blank",
        ),
        Index(
            "uq_attempts_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("submitted_at IS NULL AND closed_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problems.id", ondelete="RESTRICT"), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    answer_viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[str | None] = mapped_column(Text)
    format_understanding_before: Mapped[int | None] = mapped_column(SmallInteger)
    format_understanding_after: Mapped[int | None] = mapped_column(SmallInteger)
    scheduled_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    scheduler_version: Mapped[str | None] = mapped_column(Text)


class AttemptKnowledgeFeedback(Base):
    __tablename__ = "attempt_knowledge_feedback"
    __table_args__ = (
        CheckConstraint(
            "understanding_before BETWEEN 1 AND 5",
            name="ck_feedback_understanding_before",
        ),
        CheckConstraint(
            "understanding_after BETWEEN 1 AND 5",
            name="ck_feedback_understanding_after",
        ),
    )

    attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey("attempts.id", ondelete="RESTRICT"), primary_key=True
    )
    knowledge_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_elements.id", ondelete="RESTRICT"), primary_key=True
    )
    understood: Mapped[bool] = mapped_column(Boolean, nullable=False)
    understanding_before: Mapped[int | None] = mapped_column(SmallInteger)
    understanding_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class UserProblemReviewState(Base):
    __tablename__ = "user_problem_review_states"
    __table_args__ = (
        CheckConstraint(
            "scheduler_version ~ '[^[:space:]]'",
            name="ck_review_scheduler_not_blank",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    problem_id: Mapped[UUID] = mapped_column(
        ForeignKey("problems.id", ondelete="RESTRICT"), primary_key=True
    )
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduler_version: Mapped[str] = mapped_column(Text, nullable=False)
    last_attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey("attempts.id", ondelete="RESTRICT"), nullable=False
    )


class UnderstandingChange(Base):
    __tablename__ = "understanding_changes"
    __table_args__ = (
        CheckConstraint(
            "(knowledge_id IS NOT NULL AND exam_id IS NULL AND format_id IS NULL) OR "
            "(knowledge_id IS NULL AND exam_id IS NOT NULL AND format_id IS NOT NULL)",
            name="ck_understanding_changes_target",
        ),
        CheckConstraint(
            "understanding_before BETWEEN 1 AND 5",
            name="ck_understanding_changes_before",
        ),
        CheckConstraint(
            "understanding_after BETWEEN 1 AND 5",
            name="ck_understanding_changes_after",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    knowledge_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("knowledge_elements.id", ondelete="RESTRICT")
    )
    exam_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("exams.id", ondelete="RESTRICT")
    )
    format_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("formats.id", ondelete="RESTRICT")
    )
    understanding_before: Mapped[int | None] = mapped_column(SmallInteger)
    understanding_after: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expected_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )


class AccountDeletion(Base):
    __tablename__ = "account_deletions"
    __table_args__ = (
        CheckConstraint(
            "exported_at IS NULL OR exported_at >= deleted_at",
            name="ck_account_deletions_export_time",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class LoginRegistration(Base):
    __tablename__ = "login_registrations"
    __table_args__ = (
        CheckConstraint(
            "expires_at > issued_at",
            name="ck_login_registrations_expiry",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
