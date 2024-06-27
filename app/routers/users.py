from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# own import
from app.database.postgre_db import get_session
from app.utils.security import get_current_user, get_password_hash
from app.database.models import User, UserProfile
from app.database.schemas import UserResponse, ApproveUserRequest, UserCreate
from app.database.crud import get_superusers, create_user_and_profile

router = APIRouter()


@router.get("/get_all_users", response_model=List[UserResponse])
async def all_users(current_user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_session),):

    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.get("/get_all_superusers", response_model=List[UserResponse])
async def all_superusers(current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_session),):

    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    superusers = await get_superusers(db)

    return superusers


@router.post("/approve_user")
async def approve(request: ApproveUserRequest,
                  current_user: User = Depends(get_current_user),
                  db: AsyncSession = Depends(get_session)):

    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    query = select(User).filter(User.email == request.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.approved = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": f"User {user.email} approved successfully"}


@router.post("/create_new_user")
async def create_user(user_create: UserCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):

    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    hashed_password = get_password_hash(user_create.password)

    db_user = await create_user_and_profile(db, user_create.email, hashed_password, user_create.role)

    return {"message": f"{db_user.role.capitalize()} successfully registered",
            "email": str(db_user.email),
            "user_id": str(db_user.id)}

