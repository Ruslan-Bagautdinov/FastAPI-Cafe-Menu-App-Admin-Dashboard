from fastapi import HTTPException
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List,  Optional
from decimal import Decimal
import uuid
import os
import shutil

from app.database.models import (User,
                                 UserProfile,
                                 Restaurant,
                                 Category,
                                 Dish
                                 )

from app.config import MAIN_PHOTO_FOLDER


def format_extra_prices(extra: Optional[Dict]) -> Optional[Dict]:
    if extra is None:
        return None
    formatted_extra = {}
    for key, value in extra.items():
        description, price = value
        formatted_price = Decimal(str(price)).quantize(Decimal('0.01'))
        formatted_extra[key] = [description, formatted_price]
    return formatted_extra


async def crud_get_superusers(db: AsyncSession) -> List[User]:

    result = await db.execute(select(User).where(User.role == 'superuser'))
    superusers = result.scalars().all()
    return list(superusers)


async def crud_get_all_user_profiles(db: AsyncSession) -> Dict[uuid.UUID, Dict[str, Any]]:
    result = await db.execute(select(UserProfile).join(User))
    profiles = result.scalars().all()

    profile_dict = {}
    for profile in profiles:
        user_id = profile.user_id
        profile_info = {
            "id": profile.id,
            "user_id": profile.user_id,
            "restaurant_id": profile.restaurant_id,
            "restaurant_name": profile.restaurant_name,
            "restaurant_reviews": profile.restaurant_reviews,
            "restaurant_photo": profile.restaurant_photo,
            "telegram": profile.telegram,
            "rating": profile.rating,
            "restaurant_currency": profile.restaurant_currency,
            "tables_amount": profile.tables_amount
        }
        profile_dict[user_id] = profile_info

    return profile_dict


async def crud_get_user_profile_by_email(db: AsyncSession, email: str) -> Optional[UserProfile]:

    result = await db.execute(
        select(UserProfile).join(User).where(User.email == email)
    )
    profile = result.scalars().first()
    return profile


async def crud_get_restaurant_by_id(db: AsyncSession, restaurant_id: int):

    result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id)
    )
    return result.scalars().first()


async def crud_get_category_by_id(db: AsyncSession,
                             category_id):

    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalars().first()


async def crud_get_all_categories(db: AsyncSession):

    result = await db.execute(select(Category))
    return result.scalars().all()


async def crud_get_next_dish_id(db: AsyncSession):
    result = await db.execute(select(func.max(Dish.id)))
    max_id = result.scalar()
    return max_id + 1 if max_id is not None else 1


async def crud_get_dishes_by_email(db: AsyncSession, email: str) -> List[Dish]:
    profile = await crud_get_user_profile_by_email(db, email)
    if not profile:
        raise ValueError("User profile not found")

    if not profile.restaurant_id:
        raise ValueError("Restaurant ID not found for the user profile")

    result = await db.execute(select(Restaurant).where(Restaurant.id == profile.restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise ValueError("Restaurant not found for the user profile")

    result = await db.execute(select(Dish).where(Dish.restaurant_id == restaurant.id))
    dishes = result.scalars().all()

    # Format the price to two decimal places
    for dish in dishes:
        dish.price = Decimal(str(dish.price)).quantize(Decimal('0.01'))

    return list(dishes)


async def crud_get_email_for_dish(db: AsyncSession, dish_id: int):
    query = (
        select(User.email)
        .join(UserProfile, User.id == UserProfile.user_id)
        .join(Restaurant, UserProfile.restaurant_id == Restaurant.id)
        .join(Dish, Restaurant.id == Dish.restaurant_id)
        .where(Dish.id == dish_id)
    )
    result = await db.execute(query)
    return result.scalars().first()


async def crud_get_dish(db: AsyncSession, dish_id: int):
    query = select(Dish).where(Dish.id == dish_id)
    result = await db.execute(query)
    return result.scalars().first()


async def crud_create_user_and_profile(db: AsyncSession,
                                  email: str,
                                  hashed_password: str,
                                  role: str) -> User:

    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    approved = role == 'superuser'

    db_user = User(email=email, hashed_password=hashed_password, role=role, approved=approved)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    if role == 'restaurant':
        db_profile = UserProfile(user_id=db_user.id, tables_amount=0)
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)

        db_restaurant = Restaurant(
            name="Default Restaurant Name",
            rating=Decimal('0.0'),
            currency="USD",
            tables_amount=0
        )
        db.add(db_restaurant)
        await db.commit()
        await db.refresh(db_restaurant)

        db_profile.restaurant_id = db_restaurant.id
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)

        # Create a folder for the restaurant
        restaurant_folder = os.path.join(MAIN_PHOTO_FOLDER, str(db_restaurant.id))
        if not os.path.exists(restaurant_folder):
            os.makedirs(restaurant_folder)

    return db_user


async def crud_update_user_profile_by_email(db: AsyncSession, email: str, profile_update: dict):
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
            if profile_update.get('restaurant_reviews') is not None:
                restaurant.reviews = profile_update['restaurant_reviews']
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


async def crud_delete_user_and_profile(db: AsyncSession,
                                  email: str):

    query = select(User).filter(User.email == email).options(selectinload(User.profile).selectinload(UserProfile.restaurant))
    result = await db.execute(query)
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.profile and db_user.profile.restaurant_id:
        restaurant_query = delete(Restaurant).where(Restaurant.id == db_user.profile.restaurant_id)
        await db.execute(restaurant_query)

        # Delete the restaurant folder
        restaurant_folder = os.path.join(MAIN_PHOTO_FOLDER, str(db_user.profile.restaurant_id))
        if os.path.exists(restaurant_folder):
            shutil.rmtree(restaurant_folder)

    user_query = delete(User).where(User.email == email)
    await db.execute(user_query)

    await db.commit()


async def crud_create_dish(db: AsyncSession,
                      email: str,
                      restaurant_id: int,  # Add restaurant_id as a parameter
                      category_id: int,
                      name: str,
                      description: str,
                      price: float,
                      photo: str = None,
                      extra: dict = None):

    restaurant = await crud_get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise ValueError("Restaurant not found")

    category = await crud_get_category_by_id(db, category_id)
    if not category:
        raise ValueError("Category not found")

    next_id = await crud_get_next_dish_id(db)

    # Convert the price to Decimal and then back to float
    price_decimal = Decimal(str(price)).quantize(Decimal('0.01'))
    price_float = float(price_decimal)

    dish = Dish(
        id=next_id,
        restaurant_id=restaurant_id,
        category_id=category_id,
        name=name,
        photo=photo,
        description=description,
        price=price_float,
        extra=extra
    )
    db.add(dish)
    await db.commit()
    await db.refresh(dish)
    return dish


async def crud_update_dish(db: AsyncSession,
                      dish_id,
                      current_user: User,
                      restaurant_id=None,
                      name=None,
                      description=None,
                      price=None,
                      photo=None,
                      extra=None):

    result = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = result.scalars().first()
    if not dish:
        raise ValueError("Dish not found")

    if name is not None:
        dish.name = name
    if description is not None:
        dish.description = description
    if price is not None:
        price_decimal = Decimal(str(price)).quantize(Decimal('0.01'))
        dish.price = float(price_decimal)
    if photo is not None:
        dish.photo = photo
    if extra is not None:
        dish.extra = extra

    # Only allow updating restaurant_id if the user is a superuser
    if restaurant_id is not None and current_user.role == 'superuser':
        dish.restaurant_id = restaurant_id

    await db.commit()
    return dish


async def crud_delete_dish(db: AsyncSession,
                            dish_id: int):

    result = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = result.scalars().first()
    if not dish:
        raise ValueError("Dish not found")

    await db.delete(dish)
    await db.commit()
