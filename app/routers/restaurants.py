from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

# own import
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.models import User, UserProfile, Restaurant

from app.database.schemas import (RestaurantsResponse,
                                  UserProfileResponse,
                                  UserProfileUpdate)

from app.database.crud import (get_all_user_profiles,
                               get_user_profile_by_email,
                               update_user_profile_by_email)

router = APIRouter()


@router.get("/get_all_restaurants", response_model=RestaurantsResponse)
async def all_restaurants(current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_session)):

    if current_user.role != 'superuser':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can access this endpoint")

    restaurants = await get_all_user_profiles(db)

    return {"root": restaurants}


@router.get("/get_restaurant", response_model=Optional[UserProfileResponse])
async def get_profile_by_email(email: str,
                               current_user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_session)):

    if current_user.role == 'superuser' or current_user.email == email:
        profile = await get_user_profile_by_email(db, email)
        if profile:
            return UserProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                restaurant_id=profile.restaurant_id,
                restaurant_name=profile.restaurant_name,
                restaurant_photo=profile.restaurant_photo,
                telegram=profile.telegram,
                rating=profile.rating,
                restaurant_currency=profile.restaurant_currency,
                tables_amount=profile.tables_amount
            )
        return None

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

@router.put("/update_restaurant", response_model=Optional[UserProfileResponse])
async def update_profile_by_email(email: str,
                                  profile_update: UserProfileUpdate,
                                  current_user: User = Depends(get_current_user),
                                  db: AsyncSession = Depends(get_session)):

    if current_user.role == 'superuser' or current_user.email == email:
        profile = await update_user_profile_by_email(db, email, profile_update.dict(exclude_unset=True))
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return profile

