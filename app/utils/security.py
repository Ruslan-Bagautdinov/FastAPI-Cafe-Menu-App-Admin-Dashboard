from fastapi import (HTTPException,
                     Request,
                     Depends,
                     status,
                     Security
                     )

from fastapi.security import (OAuth2PasswordBearer,
                              HTTPBearer,
                              HTTPAuthorizationCredentials
                              )

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

# Own import
from app.database.postgre_db import get_session
from app.database.models import User
from app.config import (SECRET_KEY,
                        ALGORITHM,
                        ACCESS_TOKEN_EXPIRE_MINUTES
                        )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

security = HTTPBearer()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except PyJWTError:
#         raise credentials_exception
#
#     user = await db.execute(select(User).filter(User.email == email))
#     user = user.scalars().first()
#     if user is None:
#         raise credentials_exception
#
#     return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security),
                           db: AsyncSession = Depends(get_session)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")

    user = await db.execute(select(User).filter(User.email == email))
    user = user.scalars().first()
    if user is None:
        raise credentials_exception

    return user


async def check_existing_token(request: Request, db: AsyncSession = Depends(get_session)):
    authorization: str = request.headers.get("Authorization")
    if authorization:
        try:
            scheme, credentials = authorization.split()
            if scheme.lower() == "bearer":
                token = credentials
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email: str = payload.get("sub")
                if email is None:
                    raise HTTPException(status_code=403, detail="Invalid authentication credentials")
                user = await db.execute(select(User).filter(User.email == email))
                user = user.scalars().first()
                if user is None:
                    raise HTTPException(status_code=403, detail="Invalid authentication credentials")
                return user
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid authentication credentials")
    return None
