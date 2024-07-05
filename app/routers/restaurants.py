from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal, InvalidOperation

# Own imports
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.models import User

from app.database.schemas import (RestaurantsResponse,
                                  UserProfileResponse,
                                  UserProfileUpdate)

from app.database.crud import (crud_get_all_user_profiles,
                               crud_get_user_profile_by_email,
                               crud_update_user_profile_by_email)

router = APIRouter()


@router.get("/get_all_restaurants", response_model=RestaurantsResponse, description="Retrieve all restaurants for superusers.")
async def all_restaurants(current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_session)):
    """
    Retrieve all restaurants for superusers. (Only for superusers).

    Args:
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        RestaurantsResponse: A response containing all restaurants.

    Raises:
        HTTPException: 403 Forbidden if the current user is not a superuser.
    """
    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    restaurants = await crud_get_all_user_profiles(db)

    return {"root": restaurants}


@router.get("/get_restaurant", response_model=Optional[UserProfileResponse], description="Retrieve a user profile by email.")
async def get_profile_by_email(email: str,
                               current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_session)):
    """
    Retrieve a user profile by email.

    Args:
        email (str): The email of the user whose profile is to be retrieved.
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        Optional[UserProfileResponse]: The user profile if found, otherwise None.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to access this profile.
    """
    if current_user.role == 'superuser' or current_user.email == email:
        profile = await crud_get_user_profile_by_email(db, email)
        if profile:
            return UserProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                restaurant_id=profile.restaurant_id,
                restaurant_name=profile.restaurant_name,
                restaurant_reviews=profile.restaurant_reviews,
                restaurant_photo=profile.restaurant_photo,
                telegram=profile.telegram,
                rating=profile.rating,
                restaurant_currency=profile.restaurant_currency,
                tables_amount=profile.tables_amount
            )
        return None

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.patch("/update_restaurant", response_model=Optional[UserProfileResponse],
              description="Update a user profile by email.")
async def update_profile_by_email(email: str,
                                  profile_update: UserProfileUpdate,
                                  current_user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session)):
    """
    Update a user profile by email.

    Args:
        email (str): The email of the user whose profile is to be updated.
        profile_update (UserProfileUpdate): The updated profile data.
        current_user (User): The current authenticated user, obtained from the dependency.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        Optional[UserProfileResponse]: The updated user profile if found, otherwise None.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to update this profile.
        HTTPException: 404 Not Found if the profile is not found.
        HTTPException: 400 Bad Request if the rating value is out of range.
    """
    if current_user.role == 'superuser' or current_user.email == email:
        profile_data = profile_update.dict(exclude_unset=True)

        # Validate the rating value
        if 'rating' in profile_data:
            try:
                rating = Decimal(profile_data['rating'])
                if rating < Decimal('0.0') or rating > Decimal('9.9'):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating value out of range")
            except InvalidOperation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rating value")

        profile = await crud_update_user_profile_by_email(db, email, profile_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return profile
