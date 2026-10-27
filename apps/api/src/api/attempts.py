import stat
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth import get_current_user_id, web_origin
from api.db import engine
from api.models import (
    Attempt,
    Exam,
    KnowledgeElement,
    Problem,
    ProblemKnowledge,
    User,
)

router = APIRouter(prefix="/api/attempts", tags=["attempts"])
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]


class NextAttemptInput(BaseModel):
    id: UUID
    exam_id: UUID


def check_origin(request: Request):
    if request.headers.get("origin") != web_origin:  # originは転送元のURL
        raise HTTPException(
            status_code=403, detail="Invalid origin"
        )  # raiseはfastapiが拾えるエラーを出す。


def lock_user(session: Session, user_id: UUID):
    user = session.scalar(select(User).where(User.id == user_id).with_for_update())
    if user is None or user.google_sub is None:
        raise HTTPException(status_code=401, detail="Login required")


def owned_attempt(session: Session, attempt_id: UUID, user_id: UUID):
    attempt = session.get(Attempt, attempt_id)
    if attempt is None or attempt.user_id != user_id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


def attempt_view(session: Session, attempt: Attempt):
    problem = session.get(Problem, attempt.problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    # この問題に紐付いた知識のID・名称を取得する。
    # 本文やコストは評価対象の一覧には不要なので取得しない。
    # SQLAlchemyのJOINに任せ、知識ごとの個別問い合わせを避ける。
    knowledge_rows = (
        session.execute(
            select(
                KnowledgeElement.id,
                KnowledgeElement.title,
            )
            .join(
                ProblemKnowledge,
                ProblemKnowledge.knowledge_id == KnowledgeElement.id,
            )
            .where(ProblemKnowledge.problem_id == problem.id)
            # 同名の知識があっても表示順が安定するよう、IDも使う。
            .order_by(KnowledgeElement.title, KnowledgeElement.id)
        )
        .mappings()
        .all()
    )

    # JSONに変換できる辞書の配列へまとめる。
    # 閲覧前には知識名もヒントになるため、空配列を返す。
    # 解答閲覧後のGETで、評価対象を取得できる。
    knowledge_elements = (
        [dict(row) for row in knowledge_rows]
        if attempt.answer_viewed_at is not None
        else []
    )
    return {
        "id": attempt.id,
        "exam_id": problem.exam_id,
        "problem_id": problem.id,
        "body_md": problem.body_md,
        "started_at": attempt.started_at,
        "answer_viewed_at": attempt.answer_viewed_at,
        "submitted_at": attempt.submitted_at,
        "closed_at": attempt.closed_at,
        # 閲覧記録がある演習では、再読み込み後も解答を表示できるようにする。
        # 未閲覧ならNoneを返し、本文取得だけで解答が届くことを防ぐ。
        # 所有者確認は、この関数を呼び出す各エンドポイントで行う。
        "answer_md": (
            problem.answer_md if attempt.answer_viewed_at is not None else None
        ),
        # 解説も解答と同じ閲覧条件にする。
        # JSONでは未閲覧のNoneがnullになる。
        "explanation_md": (
            problem.explanation_md if attempt.answer_viewed_at is not None else None
        ),
        # 評価対象となる知識の配列。
        # 各要素は {"id": UUID, "title": str} の形で返す。
        "knowledge_elements": knowledge_elements,
    }


@router.post("/next")
def next_attempt(
    data: NextAttemptInput,  # Baseを継承したクラスを引数に入れると、勝手にpydanticが読み取る。
    request: Request,
    response: Response,
    user_id: CurrentUserId,
):
    check_origin(request)
    response.headers["Cache-Control"] = "no-store"

    with Session(engine) as session, session.begin():
        lock_user(session, user_id)

        existing = session.get(Attempt, data.id)
        if existing is not None:
            existing = owned_attempt(session, data.id, user_id)
            problem = session.get(Problem, existing.problem_id)
            if problem is None:
                raise HTTPException(status_code=404, detail="Problem not found")
            elif problem.exam_id != data.exam_id:
                raise HTTPException(status_code=409, detail="Operation ID reused")
            return attempt_view(session, existing)

        active = session.scalar(
            select(Attempt).where(
                Attempt.user_id == user_id,
                Attempt.submitted_at.is_(None),
                Attempt.closed_at.is_(None),
            )
        )
        if active is not None:
            raise HTTPException(
                status_code=409,
                detail={"active_attempt_id": str(active.id)},
            )

        if session.get(Exam, data.exam_id) is None:
            raise HTTPException(status_code=404, detail="Exam not found")

        problem = session.scalar(
            select(Problem)
            .where(Problem.exam_id == data.exam_id, Problem.retired_at.is_(None))
            .order_by(Problem.id)
            .limit(1)
            .with_for_update()
        )
        if problem is None:
            return {"id": None, "reason": "no_problems"}

        attempt = Attempt(id=data.id, user_id=user_id, problem_id=problem.id)
        session.add(attempt)
        session.flush()
        return attempt_view(session, attempt)


@router.get("/{attempt_id}")
def get_attempt(attempt_id: UUID, response: Response, user_id: CurrentUserId):
    response.headers["Cache-Control"] = "no-store"
    with Session(engine) as session:
        attempt = owned_attempt(session, attempt_id, user_id)
        return attempt_view(session, attempt)


@router.post("/{attempt_id}/start")
def start_attempt(
    attempt_id: UUID,
    request: Request,
    response: Response,
    user_id: CurrentUserId,
):
    check_origin(request)
    response.headers["Cache-Control"] = "no-store"

    with Session(engine) as session, session.begin():
        lock_user(session, user_id)
        attempt = owned_attempt(session, attempt_id, user_id)
        if attempt.submitted_at is not None or attempt.closed_at is not None:
            raise HTTPException(status_code=409, detail="Attempt is finished")

        if attempt.started_at is None:
            attempt.started_at = datetime.now(timezone.utc)

        return attempt_view(session, attempt)


# 解答閲覧はDBの時刻を更新するため、GETではなくPOSTで公開する。
# routerのprefixと合わせて /api/attempts/{attempt_id}/answer になる。
# ルーティング・引数検証・JSONへの変換はFastAPIに任せる。
@router.post("/{attempt_id}/answer")
def reveal_answer(
    # URLで指定された演習のID。
    # DBの主キーがUUIDなので、ここでもUUID型で受け取る。
    # UUIDとして不正な文字列はFastAPIが検証エラーにする。
    attempt_id: UUID,
    # 送信元のOriginヘッダーを確認するためのリクエスト情報。
    request: Request,
    # FastAPIが返すレスポンスに、キャッシュ制御ヘッダーを設定する。
    response: Response,
    # CurrentUserIdのDependsにより取得する、ログイン中の内部ユーザーID。
    # クライアントが任意に指定する値ではなく、認証処理の結果を使う。
    user_id: CurrentUserId,
):
    """
    自分の進行中の演習について、初回の解答閲覧時刻を記録する。

    戻り値は演習ID、閲覧時刻、Markdown形式の解答・解説。
    同じ演習で再実行した場合も、初回の閲覧時刻を保持して返す。
    理解度の更新や演習の確定は、この関数では行わない。
    """

    # Cookie認証による更新操作なので、許可したWebのOriginか確認する。
    # Originは「http://localhost:3000」のような値で、パスを含まない。
    # この確認は手書きするが、比較処理は既存の共通関数へまとめている。
    check_origin(request)

    # 個人の演習状態を含むので、ブラウザーや中継サーバーに保存させない。
    response.headers["Cache-Control"] = "no-store"

    # SessionはSQLAlchemyが提供する、DB操作と変更追跡の管理単位。
    # engineは既存の接続設定を使うため、ここで接続情報を組み立てない。
    # session.begin()は正常終了時にcommit、例外発生時にrollbackする。
    # 接続・トランザクション管理はライブラリに任せ、
    # 「いつ解答を開けるか」というアプリ固有の判断を以下に書く。
    with Session(engine) as session, session.begin():
        # ユーザー行をロックし、同じユーザーの更新操作を直列化する。
        # 開始・終了などの処理も同じロックを使うことで競合を防ぐ。
        # ロック取得後、Googleとの紐付けが残っていることも再確認する。
        lock_user(session, user_id)

        # 演習レコードを取得し、ログイン中のユーザーが所有者か確認する。
        # 存在しない場合と他人の演習の場合は、どちらも404にする。
        attempt = owned_attempt(session, attempt_id, user_id)

        # submitted_atは評価確定時刻、closed_atは未確定で終了した時刻。
        # どちらかが記録済みなら、進行中の演習としての操作は受け付けない。
        # 409は、現在の演習状態と要求された操作が両立しないことを表す。
        if attempt.submitted_at is not None or attempt.closed_at is not None:
            raise HTTPException(
                status_code=409,
                detail="Attempt is finished",
            )

        # started_atがNoneなら、まだ開始時刻が記録されていない。
        # 閲覧時刻が開始時刻より前になることを防ぐため、先に開始を要求する。
        if attempt.started_at is None:
            raise HTTPException(
                status_code=409,
                detail="Attempt is not started",
            )

        # 演習に紐付いた問題を主キーで取得する。
        # Session.getを使い、主キー検索をSQLAlchemyに任せる。
        # 問題が利用停止済みでも、既存の演習ではその問題を参照する。
        problem = session.get(Problem, attempt.problem_id)
        if problem is None:
            raise HTTPException(
                status_code=404,
                detail="Problem not found",
            )

        # answer_viewed_atは、APIが初回の解答閲覧要求を処理した時刻。
        # UTC・タイムゾーン付きdatetimeで、DBの日時型に合わせる。
        # ブラウザーが申告した時刻ではなく、API側で生成する。
        # 連打や通信失敗後の再試行でも、初回の値は上書きしない。
        if attempt.answer_viewed_at is None:
            attempt.answer_viewed_at = datetime.now(timezone.utc)

        # UUIDとdatetimeのJSON変換はFastAPIに任せる。
        # DBのcommit完了後にレスポンスが返る。
        return {
            # フロント側で、どの演習の解答か識別するためのID。
            "id": attempt.id,
            # JSONではタイムゾーン付きの日時文字列になる。
            # 初回の記録、再開時の表示、後の所要時間計算に使う。
            "answer_viewed_at": attempt.answer_viewed_at,
            # 問題に保存してあるMarkdown形式の模範解答。
            "answer_md": problem.answer_md,
            # 問題に保存してあるMarkdown形式の解説。
            "explanation_md": problem.explanation_md,
        }
