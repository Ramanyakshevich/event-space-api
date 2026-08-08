from datetime import timedelta, datetime, timezone
from typing import Dict, Any, Optional

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from core.config import settings

password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_jwt_token(
        data: Dict[str, Any],
        expires_delta: timedelta,
        token_type: str = "access"
) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": token_type
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_access_token(subject: str | int, role: str) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(
        data={"sub": str(subject), "role": role},
        expires_delta=expires_delta,
        token_type="access"
    )

def create_refresh_token(subject: str | int) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_jwt_token(
        data={"sub": str(subject)},
        expires_delta=expires_delta,
        token_type="refresh"
    )

def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None

