from fastapi import (APIRouter,
                     Request,
                     Depends,
                     HTTPException,
                     status
                     )
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Own imports
from app.database.postgre_db import get_session
from app.database.models import User, UserProfile
from app.database.schemas import UserRegister, UserCreate, UserLogin
from app.database.crud import crud_create_user_and_profile
from app.utils.security import (get_password_hash,
                                verify_password,
                                create_access_token,
                                check_existing_token
                                )


router = APIRouter()


# @router.post("/login", description="Authenticates a user and returns an access token.")
# async def login(userlogin: UserLogin,
#                 db: AsyncSession = Depends(get_session)):
#     """
#     Authenticates a user and returns an access token.
#
#     Args:
#         userlogin (UserLogin): The user login data containing email and password.
#         db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
#
#     Returns:
#         dict: A dictionary containing the access token and token type.
#
#     Raises:
#         HTTPException: 401 Unauthorized if the email or password is invalid.
#         HTTPException: 403 Forbidden if the user role is not 'superuser' or 'restaurant'.
#     """
#     user = await db.execute(select(User).filter(User.email == userlogin.email))
#     user = user.scalars().first()
#
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Invalid email or password")
#
#     if not verify_password(userlogin.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Invalid email or password")
#
#     if user.role not in ['superuser', 'restaurant']:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="Incorrect role for user")
#
#     access_token = create_access_token(data={"sub": user.email, "role": user.role})
#
#     return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", description="Authenticates a user and returns an access token.")
async def login(userlogin: UserLogin,
                request: Request,
                db: AsyncSession = Depends(get_session)):
    """
    Authenticates a user and returns an access token.

    Args:
        userlogin (UserLogin): The user login data containing email and password.
        request (Request): The incoming request object.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: 401 Unauthorized if the email or password is invalid.
        HTTPException: 403 Forbidden if the user role is not 'superuser' or 'restaurant'.
        HTTPException: 400 Bad Request if the user is already authenticated.
    """
    current_user = await check_existing_token(request, db)
    if current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User is already authenticated. Please log out first.")

    user = await db.execute(select(User).filter(User.email == userlogin.email))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if not verify_password(userlogin.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if user.role not in ['superuser', 'restaurant']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Incorrect role for user")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}


# @router.post("/register", description="Registers a new user and returns registration details.")
# async def register_user(user_register: UserRegister,
#                         db: AsyncSession = Depends(get_session)):
#     """
#     Registers a new user and returns registration details.
#
#     Args:
#         user_register (UserRegister): The user registration data containing email and password.
#         db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.
#
#     Returns:
#         dict: A dictionary containing a success message, user email, and user ID.
#     """
#     hashed_password = get_password_hash(user_register.password)
#
#     db_user = await create_user_and_profile(db, user_register.email, hashed_password, "restaurant")
#
#     return {"message": f"{db_user.role.capitalize()} successfully registered",
#             "email": str(db_user.email),
#             "user_id": str(db_user.id)}


@router.post("/register", description="Registers a new user and returns registration details.")
async def register_user(user_register: UserRegister,
                        request: Request,
                        db: AsyncSession = Depends(get_session)):
    """
    Registers a new user and returns registration details.

    Args:
        user_register (UserRegister): The user registration data containing email and password.
        request (Request): The incoming request object.
        db (AsyncSession): The SQLAlchemy asynchronous session, obtained from the dependency.

    Returns:
        dict: A dictionary containing a success message, user email, and user ID.

    Raises:
        HTTPException: 400 Bad Request if the user is already authenticated.
    """
    current_user = await check_existing_token(request, db)
    if current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User is already authenticated. Please log out first.")

    hashed_password = get_password_hash(user_register.password)

    db_user = await crud_create_user_and_profile(db, user_register.email, hashed_password, "restaurant")

    return {"message": f"{db_user.role.capitalize()} successfully registered",
            "email": str(db_user.email),
            "user_id": str(db_user.id)}
