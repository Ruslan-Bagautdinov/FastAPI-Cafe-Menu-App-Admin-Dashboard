from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


# own import
from app.database.postgre_db import get_session
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.database.models import User, UserProfile
from app.database.schemas import UserRegister, UserCreate, UserLogin
from app.database.crud import create_user_and_profile

router = APIRouter()


@router.post("/login")
async def login(userlogin: UserLogin,
                db: AsyncSession = Depends(get_session)):

    user = await db.execute(select(User).filter(User.email == userlogin.email))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if not verify_password(userlogin.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if user.role not in ['superuser', 'restaurant']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Incorrect role for user")

    # if not user.approved:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="User not approved")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(user_register: UserRegister,
                        db: AsyncSession = Depends(get_session)):

    hashed_password = get_password_hash(user_register.password)

    db_user = await create_user_and_profile(db, user_register.email, hashed_password, "restaurant")

    return {"message": f"{db_user.role.capitalize()} successfully registered",
            "email": str(db_user.email),
            "user_id": str(db_user.id)}
