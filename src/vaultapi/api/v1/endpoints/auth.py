from fastapi import APIRouter, Depends, status, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.vaultapi.db.session import get_db
from src.vaultapi.schemas.user import UserCreate, UserLogin, UserResponse
from src.vaultapi.schemas.token import Token, RefreshTokenRequest
from src.vaultapi.services.auth import (
    register_user,
    authenticate_user,
    generate_and_save_tokens,
)

from src.vaultapi.models.user import User
from src.vaultapi.core.deps import get_current_user

from src.vaultapi.core.security import decode_token
from src.vaultapi.models.refresh_token import RefreshToken

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, user_data.email, user_data.password)
    tokens = await generate_and_save_tokens(db, user)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
    )

    return {"access_token": tokens["access_token"], "token_type": tokens["token_type"]}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str = Cookie(None),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    try:
        payload = decode_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

    user_id = payload.get("sub")

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked or invalid"
        )

    db_token.revoked = True
    await db.commit()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    tokens = await generate_and_save_tokens(db, user)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
    )

    return {"access_token": tokens["access_token"], "token_type": tokens["token_type"]}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
