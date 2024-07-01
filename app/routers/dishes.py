from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# own import
from app.database.models import (User,
                                 UserProfile,
                                 Restaurant,
                                 Dish,
                                 Category
                                 )
from app.database.schemas import (DishResponse,
                                  DishCreate,
                                  DishUpdate,
                                  DishDelete
                                  )
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.crud import (create_dish,
                               update_dish,
                               delete_dish, get_dishes_by_email
                               )

router = APIRouter()


@router.post("/dishes/email/", response_model=list[DishResponse])
async def get_dishes_by_email_handler(
    email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
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
                extra=dish.extra
            ) for dish in dishes]
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view dishes for this email.")


@router.post("/dishes/", response_model=DishResponse)
async def get_dish_by_id_handler(
        dish_id: int = Body(..., embed=True),
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Join the necessary tables to fetch the email
    query = (
        select(Dish, User.email)
        .join(Restaurant, Dish.restaurant_id == Restaurant.id)
        .join(UserProfile, Restaurant.id == UserProfile.restaurant_id)
        .join(User, UserProfile.user_id == User.id)
        .where(Dish.id == dish_id)
    )

    result = await db.execute(query)
    dish, email = result.first()

    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    if current_user.role == 'superuser' or current_user.email == email:
        return DishResponse(
            id=dish.id,
            restaurant_id=dish.restaurant_id,
            category_id=dish.category_id,
            name=dish.name,
            photo=dish.photo,
            description=dish.description,
            price=dish.price,
            extra=dish.extra
        )
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view this dish.")


@router.post("/create/", response_model=DishResponse)
async def create_dish_handler(
    dish: DishCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if current_user.role == 'superuser' or current_user.email == dish.email:
        try:
            created_dish = await create_dish(
                db,
                email=dish.email,
                category_id=dish.category_id,
                name=dish.name,
                description=dish.description,
                price=dish.price,
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
                extra=created_dish.extra
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create a dish for this email.")


@router.put("/update/", response_model=DishResponse)
async def update_dish_handler(
    dish: DishUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == 'superuser' or current_user.email == dish.email:
        try:
            updated_dish = await update_dish(
                db,
                dish_id=dish.dish_id,
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
                extra=updated_dish.extra
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    else:
        raise HTTPException(status_code=403, detail="You do not have permission to update a dish for this email.")


@router.delete("/delete/")
async def delete_dish_handler(
    dish: DishDelete,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == 'superuser' or current_user.email == dish.email:
        try:
            await delete_dish(db, dish_id=dish.dish_id)
            return {"message": f"Dish {dish.dish_id} deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete a dish for this email.")
