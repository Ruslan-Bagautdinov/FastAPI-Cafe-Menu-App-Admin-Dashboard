from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


# own import
from app.database.postgre_db import get_session
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.database.models import User, UserProfile
from app.database.schemas import UserCreate, UserLogin

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

    if not user.approved or user.role not in ['superuser', 'restaurant']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User not approved or incorrect role")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(user_create: UserCreate,
                        db: AsyncSession = Depends(get_session)):

    query = select(User).filter(User.email == user_create.email)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Email already registered")

    hashed_password = get_password_hash(user_create.password)

    db_user = User(email=user_create.email,
                   hashed_password=hashed_password,
                   role="restaurant")
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create the UserProfile
    db_profile = UserProfile(user_id=db_user.id)
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return {"message": "User successfully registered",
            "user_id": str(db_user.id)
            }
