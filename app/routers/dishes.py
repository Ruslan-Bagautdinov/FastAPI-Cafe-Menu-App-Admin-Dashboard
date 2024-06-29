from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


# own import
from app.database.models import User
from app.database.schemas import (DishResponse,
                                  DishCreate,
                                  DishUpdate,
                                  DishDelete)
from app.database.postgre_db import get_session
from app.utils.security import get_current_user
from app.database.crud import create_dish, update_dish, delete_dish

router = APIRouter()


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
    if current_user.role != 'superuser' and current_user.email != dish.email:
        raise HTTPException(status_code=403, detail="You do not have permission to update a dish for this email.")

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


@router.delete("/delete/")
async def delete_dish_handler(
    dish: DishDelete,
    db: AsyncSession = Depends(get_session)
):
    try:
        await delete_dish(db, dish_id=dish.dish_id)
        return {"message": "Dish deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
