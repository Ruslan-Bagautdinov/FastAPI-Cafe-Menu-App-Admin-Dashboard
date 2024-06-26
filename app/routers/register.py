from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select


# own import
from app.database.postgre_db import get_session
from app.utils.security import get_password_hash

from app.database.models import User, UserProfile
from app.database.schemas import UserCreate


router = APIRouter()


@router.post("/register/")
async def register_user(user_create: UserCreate, db: AsyncSession = Depends(get_session)):
    # Check if user already exists
    query = select(User).filter(User.email == user_create.email)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = get_password_hash(user_create.password)

    # Create the User with the role "restaurant"
    db_user = User(email=user_create.email, hashed_password=hashed_password, role="restaurant")
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create the UserProfile
    db_profile = UserProfile(user_id=db_user.id)
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return {"message": "User successfully registered", "user_id": str(db_user.id)}
