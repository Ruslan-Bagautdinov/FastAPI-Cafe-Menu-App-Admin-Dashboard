from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

# Own imports
from app.database.models import User, UserProfile, Dish
from app.database.schemas import (DishResponse,
                                  DishCreate,
                                  DishUpdate,
                                  DishDelete
                                  )
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.crud import (crud_create_dish,
                               crud_update_dish,
                               crud_delete_dish,
                               crud_get_restaurant_by_id,
                               crud_get_dishes_by_email,
                               crud_get_email_for_dish,
                               crud_get_dish,
                               format_extra_prices,
                               crud_get_user_profile_by_email,
                               crud_get_category_id_name_pairs,
                               crud_get_all_categories

                               )

router = APIRouter()


@router.get("/all_categories/",
             description="Retrieve a dictionary mapping category IDs to their names.")
async def get_id_category_pairs(
        db: AsyncSession = Depends(get_session)
):
    """
    Retrieves a dictionary mapping category IDs to their names for a specified restaurant or all categories if no restaurant is specified.

    Args:
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A dictionary where keys are category IDs and values are category names.
    """

    pairs = await crud_get_category_id_name_pairs(db)
    return pairs


@router.post("/categories_in_restaurant/", description="Retrieve categories used in a restaurant linked with the user's email.")
async def get_categories_in_restaurant(
        email: str = Body(..., embed=True),
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve categories used in a restaurant linked with the user's email.

    Args:
        email (str): The email of the user whose linked restaurant's categories are to be retrieved.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        CategoryResponse: The categories used in the restaurant linked with the user's email.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to view these categories.
        HTTPException: 404 Not Found if the user profile or restaurant is not found.
    """
    profile = await crud_get_user_profile_by_email(db, email)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    if profile.restaurant_id is None:
        raise HTTPException(status_code=404, detail="Restaurant not found for the user")

    if current_user.role != 'superuser' and current_user.email != email:
        raise HTTPException(status_code=403, detail="You do not have permission to view these categories.")

    category_id_name_pairs = await crud_get_category_id_name_pairs(db, profile.restaurant_id)

    return category_id_name_pairs
    # return CategoryResponse(categories=category_id_name_pairs)


@router.post("/dish_by_id/", response_model=DishResponse, description="Retrieve a dish by its ID.")
async def get_dish_by_id(
        dish_id: int = Body(..., embed=True),
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve a dish by its ID.

    Args:
        dish_id (int): The ID of the dish to be retrieved.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        DishResponse: The dish associated with the given ID.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to view this dish.
        HTTPException: 404 Not Found if the dish is not found.
    """
    dish = await crud_get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    email = await crud_get_email_for_dish(db, dish_id)

    if current_user.role == 'superuser' or current_user.email == email:
        return DishResponse(
            id=dish.id,
            restaurant_id=dish.restaurant_id,
            category_id=dish.category_id,
            name=dish.name,
            photo=dish.photo,
            description=dish.description,
            price=Decimal(str(dish.price)).quantize(Decimal('0.01')),
            extra=format_extra_prices(dish.extra)
        )
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view this dish.")


@router.post("/create/", response_model=DishResponse, description="Create a new dish.")
async def create_new_dish(
    dish: DishCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new dish.

    Args:
        dish (DishCreate): The dish creation data.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        DishResponse: The created dish.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to create a dish for this email.
        HTTPException: 400 Bad Request if an error occurs while creating the dish.
    """
    if current_user.role == 'superuser' or current_user.email == dish.email:
        try:
            # For superusers, use the provided restaurant_id
            if current_user.role == 'superuser':
                restaurant_id = dish.restaurant_id
            else:
                # For restaurant role, fetch restaurant_id from user profile
                profile = await crud_get_user_profile_by_email(db, current_user.email)
                if not profile or not profile.restaurant_id:
                    raise HTTPException(status_code=400, detail="Restaurant ID not found for the user profile.")
                restaurant_id = profile.restaurant_id

            created_dish = await crud_create_dish(
                db,
                email=dish.email,
                restaurant_id=restaurant_id,
                category_id=dish.category_id,
                name=dish.name,
                description=dish.description,
                price=float(dish.price),
                photo=dish.photo,
                extra=dish.extra
            )
            return DishResponse(
                id=created_dish.id,
                restaurant_id=created_dish.restaurant_id,
                category_id=created_dish.category_id,
                name=created_dish.name,
                photo=created_dish.photo,
                description=created_dish.description,
                price=created_dish.price,
                extra=format_extra_prices(created_dish.extra)
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create a dish for this email.")


@router.patch("/update/", response_model=DishResponse, description="Update an existing dish.")
async def update_dish_route(
    dish: DishUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing dish.

    Args:
        dish (DishUpdate): The dish update data.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        DishResponse: The updated dish.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to update a dish for this email.
        HTTPException: 404 Not Found if an error occurs while updating the dish.
    """
    if current_user.role == 'superuser' or current_user.email == dish.email:
        try:
            updated_dish = await crud_update_dish(
                db,
                dish.dish_id,  # Pass dish_id as a positional argument
                current_user=current_user,  # Pass current_user to check role
                restaurant_id=dish.restaurant_id,
                name=dish.name,
                description=dish.description,
                price=dish.price,
                photo=dish.photo,
                extra=dish.extra
            )
            return DishResponse(
                id=updated_dish.id,
                restaurant_id=updated_dish.restaurant_id,
                category_id=updated_dish.category_id,
                name=updated_dish.name,
                photo=updated_dish.photo,
                description=updated_dish.description,
                price=updated_dish.price,
                extra=format_extra_prices(updated_dish.extra)
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to update a dish for this email.")


@router.delete("/delete/", description="Delete a dish by its ID.")
async def delete_dish(
    dish: DishDelete,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a dish by its ID.

    Args:
        dish (DishDelete): The dish deletion data.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        dict: A message indicating the dish was deleted successfully.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to delete a dish for this email.
        HTTPException: 404 Not Found if an error occurs while deleting the dish.
    """
    if current_user.role == 'superuser' or current_user.email == dish.email:
        try:
            await crud_delete_dish(db, dish_id=dish.dish_id)
            return {"message": f"Dish {dish.dish_id} deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete a dish for this email.")


@router.post("/dishes_by_email/", response_model=List[DishResponse], description="Retrieve dishes by user email.")
async def get_dishes_by_email(
    email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve dishes by user email.

    Args:
        email (str): The email of the user whose dishes are to be retrieved.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        List[DishResponse]: The dishes associated with the user's email.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to view these dishes.
        HTTPException: 404 Not Found if the user profile or restaurant is not found.
    """
    if current_user.role == 'superuser' or current_user.email == email:
        try:
            profile = await db.execute(
                select(UserProfile).options(selectinload(UserProfile.restaurant)).join(User).where(User.email == email)
            )
            profile = profile.scalars().first()
            if not profile:
                raise HTTPException(status_code=404, detail="User profile not found")

            restaurant = profile.restaurant
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found for the user profile")

            result = await db.execute(select(Dish).where(Dish.restaurant_id == restaurant.id))
            dishes = result.scalars().all()
            return [DishResponse(
                id=dish.id,
                restaurant_id=dish.restaurant_id,
                category_id=dish.category_id,
                name=dish.name,
                photo=dish.photo,
                description=dish.description,
                price=Decimal(str(dish.price)).quantize(Decimal('0.01')),
                extra=format_extra_prices(dish.extra)
            ) for dish in dishes]
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view these dishes.")
