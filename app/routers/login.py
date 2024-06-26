from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


# own import
from app.database.postgre_db import get_session
from app.utils.security import verify_password, create_access_token

from app.database.models import User
from app.database.schemas import UserLogin


router = APIRouter()


@router.post("/login/")
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_session)):
    # Find the user by email
    query = select(User).filter(User.email == user_login.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Verify the password
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Check if the user is approved and has the correct role
    if not user.approved or user.role not in ['superuser', 'restaurant']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not approved or incorrect role")

    # Create the JWT token
    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}

