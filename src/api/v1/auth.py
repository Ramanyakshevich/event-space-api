from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import UserServiceDep, CurrentUserDep
from src.schemas.user import UserRead, UserCreate, Token, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, user_service: UserServiceDep):
    return await user_service.register(user_in)

@router.post("/login", response_model=Token)
async def login(from_data: Annotated[OAuth2PasswordRequestForm, Depends()], user_service: UserServiceDep):
    user = await user_service.authenticate(email=from_data.username, password=from_data.password)
    return await user_service.create_tokens_for_user(user)

@router.post("/refresh", response_model=Token)
async def refresh_tokens(body: RefreshTokenRequest, user_service: UserServiceDep):
    return await user_service.refresh_tokens(body.refresh_token)

@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep):
    return current_user