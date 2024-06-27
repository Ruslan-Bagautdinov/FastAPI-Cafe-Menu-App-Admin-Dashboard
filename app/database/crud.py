from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List,  Optional
from decimal import Decimal
import uuid

from app.database.models import User, UserProfile, Restaurant


async def get_superusers(session: AsyncSession) -> List[User]:
    result = await session.execute(select(User).where(User.role == 'superuser'))
    superusers = result.scalars().all()
    return list(superusers)


async def get_all_user_profiles(session: AsyncSession) -> Dict[uuid.UUID, Dict[str, Any]]:
    result = await session.execute(select(UserProfile).join(User))
    profiles = result.scalars().all()

    profile_dict = {}
    for profile in profiles:
        user_id = profile.user_id
        profile_info = {
            "id": profile.id,
            "user_id": profile.user_id,
            "restaurant_id": profile.restaurant_id,
            "restaurant_name": profile.restaurant_name,
            "restaurant_photo": profile.restaurant_photo,
            "telegram": profile.telegram,
            "rating": profile.rating,
            "restaurant_currency": profile.restaurant_currency,
            "tables_amount": profile.tables_amount
        }
        profile_dict[user_id] = profile_info

    return profile_dict


async def get_user_profile_by_email(session: AsyncSession, email: str) -> Optional[UserProfile]:
    result = await session.execute(
        select(UserProfile).join(User).where(User.email == email)
    )
    profile = result.scalars().first()
    return profile


async def create_user_and_profile(db: AsyncSession, email: str, hashed_password: str, role: str) -> User:
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Set approved to True if the role is 'superuser'
    approved = role == 'superuser'

    db_user = User(email=email, hashed_password=hashed_password, role=role, approved=approved)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    if role == 'restaurant':
        db_profile = UserProfile(user_id=db_user.id, tables_amount=0)  # Default tables_amount value
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)

        # Create a Restaurant with default values
        db_restaurant = Restaurant(
            name="Default Restaurant Name",
            rating=Decimal('0.0'),
            currency="USD",
            tables_amount=0  # Default tables_amount value
        )
        db.add(db_restaurant)
        await db.commit()
        await db.refresh(db_restaurant)

        # Update the UserProfile with the newly created Restaurant's ID
        db_profile.restaurant_id = db_restaurant.id
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)

    return db_user


async def update_user_profile_by_email(db: AsyncSession, email: str, profile_update: dict):
    query = select(UserProfile).join(User).filter(User.email == email)
    result = await db.execute(query)
    profile = result.scalars().first()

    if profile is None:
        return None

    for key, value in profile_update.items():
        setattr(profile, key, value)

    if profile.restaurant_id is not None:
        restaurant_query = select(Restaurant).filter(Restaurant.id == profile.restaurant_id)
        restaurant_result = await db.execute(restaurant_query)
        restaurant = restaurant_result.scalars().first()

        if restaurant is not None:
            if profile_update.get('restaurant_name') is not None:
                restaurant.name = profile_update['restaurant_name']
            if profile_update.get('restaurant_photo') is not None:
                restaurant.photo = profile_update['restaurant_photo']
            if profile_update.get('rating') is not None:
                restaurant.rating = Decimal(profile_update['rating'])
            if profile_update.get('restaurant_currency') is not None:
                restaurant.currency = profile_update['restaurant_currency']
            if profile_update.get('tables_amount') is not None:
                restaurant.tables_amount = profile_update['tables_amount']

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return profile
