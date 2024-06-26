from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# own import
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.models import User
from app.database.schemas import UserResponse, ApproveUserRequest


router = APIRouter()


@router.get("/get_all", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_session),):

    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.post("/approve")
async def approve_user(request: ApproveUserRequest,
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

    return {"message": "User approved successfully"}
