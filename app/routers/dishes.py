from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

# Own imports
from app.database.models import User
from app.database.schemas import (DishResponse,
                                  DishCreate,
                                  DishUpdate,
                                  DishDelete
                                  )
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.crud import (create_dish,
                               update_dish,
                               delete_dish,
                               get_dishes_by_email,
                               get_email_for_dish,
                               get_dish,
                               format_extra_prices
                               )

router = APIRouter()


@router.post("/all_dishes_by_email/", response_model=list[DishResponse], description="Retrieve all dishes by user email.")
async def get_all_dishes_by_email(
    email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all dishes by user email.

    Args:
        email (str): The email of the user whose dishes are to be retrieved.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
        current_user (User): The current authenticated user, obtained from the dependency.

    Returns:
        list[DishResponse]: A list of dishes associated with the given email.

    Raises:
        HTTPException: 403 Forbidden if the current user does not have permission to view dishes for this email.
        HTTPException: 404 Not Found if an error occurs while retrieving the dishes.
    """
    if current_user.role == 'superuser' or current_user.email == email:
        try:
            dishes = await get_dishes_by_email(db, email)
            return [DishResponse(
                id=dish.id,
                restaurant_id=dish.restaurant_id,
                category_id=dish.category_id,
                name=dish.name,
                photo=dish.photo,
                description=dish.description,
                price=dish.price,
                extra=format_extra_prices(dish.extra)
            ) for dish in dishes]
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view dishes for this email.")


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
    dish = await get_dish(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    email = await get_email_for_dish(db, dish_id)

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
            created_dish = await create_dish(
                db,
                email=dish.email,
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


@router.put("/update/", response_model=DishResponse, description="Update an existing dish.")
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
            updated_dish = await update_dish(
                db,
                dish.dish_id,  # Pass dish_id as a positional argument
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
            await delete_dish(db, dish_id=dish.dish_id)
            return {"message": f"Dish {dish.dish_id} deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete a dish for this email.")
