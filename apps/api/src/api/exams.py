from uuid import UUID

from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth import get_current_user_id
from api.db import engine
from api.models import Exam, Subject, Problem

router = APIRouter(
    prefix="/api/exams",
    tags=["exams"],
    dependencies=[Depends(get_current_user_id)],
)


class ExamSummary(BaseModel):
    id: UUID
    name: str
    category: str
    subject_id: UUID
    subject_name: str


@router.get("", response_model=list[ExamSummary])
def list_exams(response: Response):
    response.headers["Cache-Control"] = "no-store"
    statement = (
        select(
            Exam.id,
            Exam.name,
            Exam.category,
            Exam.subject_id,
            Subject.name.label("subject_name"),
        )
        .join(Subject, Exam.subject_id == Subject.id)
        .order_by(Exam.name, Exam.id)
        .limit(20)
    )

    with Session(engine) as session:
        return session.execute(statement).mappings().all()


class ProblemPreview(BaseModel):
    id: UUID
    body_md: str


class ExamDetail(ExamSummary):
    problems: list[ProblemPreview]


@router.get("/{exam_id}", response_model=ExamDetail)
def get_exam(exam_id: UUID, response: Response):
    response.headers["Cache-Control"] = "no-store"

    statement = (
        select(
            Exam.id,
            Exam.name,
            Exam.category,
            Exam.subject_id,
            Subject.name.label("subject_name"),
        )
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Exam.id == exam_id)
    )

    with Session(engine) as session:
        exam = session.execute(statement).mappings().one_or_none()
        if exam is None:
            raise HTTPException(status_code=404, detail="Exam not found")

        problems = (
            session.execute(
                select(Problem.id, Problem.body_md)
                .where(Problem.exam_id == exam_id, Problem.retired_at.is_(None))
                .order_by(Problem.id)
                .limit(50)
            )
            .mappings()
            .all()
        )

        return {**exam, "problems": problems}
