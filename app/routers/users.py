from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# Own imports
from app.database.postgre_db import get_session
from app.utils.security import get_current_user, get_password_hash
from app.database.models import User, UserProfile
from app.database.schemas import UserResponse, ApproveUserRequest, UserCreate
from app.database.crud import (get_superusers,
                               create_user_and_profile,
                               delete_user_and_profile
                               )

router = APIRouter()


@router.get("/get_all_users", response_model=List[UserResponse], description="Retrieve all users. (Only for superusers)")
async def all_users(current_user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_session)):
    """
    Retrieve all users (Only for superusers).

    Args:
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        List[UserResponse]: A list of all users.

    Raises:
        HTTPException: 403 Forbidden if the current user is not a superuser.
    """
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.get("/get_all_superusers", response_model=List[UserResponse], description="Retrieve all superusers for superusers. (Only for superusers)")
async def all_superusers(current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
    Retrieve all superusers (Only for superusers).

    Args:
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        List[UserResponse]: A list of all superusers.

    Raises:
        HTTPException: 403 Forbidden if the current user is not a superuser.
    """
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    superusers = await get_superusers(db)

    return superusers


@router.post("/approve_user", description="Approve a user by email. (Only for superusers)")
async def approve(request: ApproveUserRequest,
                  current_user: User = Depends(get_current_user),
                  db: AsyncSession = Depends(get_session)):
    """
    Approve a user by email (Only for superusers).

    Args:
        request (ApproveUserRequest): The request containing the email of the user to be approved.
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A message indicating the user was approved successfully.

    Raises:
        HTTPException: 403 Forbidden if the current user is not a superuser.
        HTTPException: 404 Not Found if the user is not found.
    """
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


@router.post("/create_new_user", description="Create a new user. (Only for superusers)")
async def create_user(user_create: UserCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    """
    Create a new user, the restaurant or the superuser (Only for superusers).

    Args:
        user_create (UserCreate): The request containing the details of the user to be created.
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A message indicating the user was created successfully, along with the user's email and ID.

    Raises:
        HTTPException: 403 Forbidden if the current user is not a superuser.
    """
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    hashed_password = get_password_hash(user_create.password)

    db_user = await create_user_and_profile(db, user_create.email, hashed_password, user_create.role)

    return {"message": f"{db_user.role.capitalize()} successfully registered",
            "email": str(db_user.email),
            "user_id": str(db_user.id)}


@router.delete("/delete_user_by_email/", description="Delete a user by email. (Only for superusers)")
async def delete_user(email: str = Body(..., embed=True), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    """
    Delete a user by email (Only for superusers).

    Args:
        email (str): The email of the user to be deleted, embedded in the body.
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A message indicating the user and associated profile and restaurant were deleted successfully.

    Raises:
        HTTPException: 403 Forbidden if the current user is not a superuser.
    """
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    await delete_user_and_profile(db, email)

    return {"message": "User and associated profile and restaurant successfully deleted"}
