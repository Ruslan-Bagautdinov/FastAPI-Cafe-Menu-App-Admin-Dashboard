from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

# own import
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.models import User
from app.database.schemas import UserResponse

router = APIRouter()


@router.get("/users/", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check if the current user is a superuser
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    # Fetch all users from the database
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    return users
