from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.vaultapi.db.session import get_db
from src.vaultapi.schemas.user import UserCreate, UserLogin, UserResponse
from src.vaultapi.schemas.token import Token
from src.vaultapi.services.auth import register_user, authenticate_user
from src.vaultapi.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authtication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, user_data.email, user_data.password)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
