from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# own import
from app.database.postgre_db import get_session
from app.utils.security import get_current_user

from app.database.schemas import ApproveUserRequest
from app.database.models import User

router = APIRouter()


@router.post("/approve-user/")
async def approve_user(request: ApproveUserRequest, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check if the current user is a superuser
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    # Find the user by email
    query = select(User).filter(User.email == request.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the user's approved status
    user.approved = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User approved successfully"}
