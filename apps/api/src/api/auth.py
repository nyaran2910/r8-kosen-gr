import os
from uuid import UUID

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from starlette.responses import RedirectResponse
from typing import Annotated

from api.db import engine
from api.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
web_origin = os.environ["WEB_ORIGIN"]

oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "code_challenge_method": "S256",
    },
)


def register_user(google_sub: str) -> str:
    statement = (
        insert(User)
        .values(google_sub=google_sub)
        .on_conflict_do_update(
            index_elements=[User.google_sub],
            set_={"google_sub": google_sub},
        )
        .returning(User.id)
    )

    with Session(engine) as session:
        user_id = session.execute(statement).scalar_one()
        session.commit()
        return str(user_id)


def get_current_user_id(request: Request) -> UUID:
    try:
        user_id = UUID(request.session["user_id"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Login required")

    with Session(engine) as session:
        user = session.get(User, user_id)
        if user is None or user.google_sub is None:
            request.session.clear()
            raise HTTPException(status_code=401, detail="Login required")

        request.session["user_id"] = str(user.id)
        return user.id


@router.get("/google/login")
async def login(request: Request):
    return await google.authorize_redirect(
        request,
        os.environ["GOOGLE_REDIRECT_URI"],
    )


@router.get("/google/callback")
async def callback(request: Request):
    try:
        token = await google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(status_code=400, detail="Google login failed")

    userinfo = token.get("userinfo")
    google_sub = userinfo.get("sub") if userinfo else None
    if not isinstance(google_sub, str) or not google_sub:
        raise HTTPException(status_code=400, detail="Invalid Google identity")

    user_id = await run_in_threadpool(register_user, google_sub)
    request.session.clear()
    request.session["user_id"] = user_id
    return RedirectResponse(web_origin, status_code=303)


@router.get("/me")
def me(
    response: Response,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    response.headers["Cache-Control"] = "no-store"
    return {"id": str(user_id)}


@router.post("/logout")
def logout(request: Request):
    if request.headers.get("origin") != web_origin:
        raise HTTPException(status_code=403, detail="Invalid origin")

    request.session.clear()
    return RedirectResponse(web_origin, status_code=303)
