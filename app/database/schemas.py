from pydantic import (BaseModel,
                      Field,
                      EmailStr,
                      condecimal,
                      field_validator,
                      model_validator
                      )
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid


class UserLogin(BaseModel):
    """
    Schema for user login.

    Attributes:
        email (EmailStr): The email address of the user (inherited from UserRegister).
        password (str): The password for the user account (inherited from UserRegister).
    """
    email: EmailStr
    password: str


class UserRegister(UserLogin):
    """
    Schema for user registration, extending from UserLogin.

    Attributes:
        email (EmailStr): The email address of the user.
        password (str): The password for the user account.
        restaurant_currency (Optional[str]): The currency of the restaurant.
        tables_amount (Optional[int]): The amount of tables available.
    """
    restaurant_currency: Optional[str] = None
    tables_amount: Optional[int] = None


class UserCreate(UserRegister):
    """
    Schema for creating a new user, extending from UserRegister.

    Attributes:
        email (EmailStr): The email address of the user (inherited from UserRegister).
        password (str): The password for the user account (inherited from UserRegister).
        role (str): The role of the user, can be 'superuser' or 'restaurant'.
        restaurant_currency (Optional[str]): The currency of the restaurant.
        tables_amount (Optional[int]): The amount of tables available.
    """
    role: str

    @field_validator('role')
    def validate_role(cls, value):
        if value not in ['superuser', 'restaurant']:
            raise ValueError("Role must be 'superuser' or 'restaurant'")
        return value


class ApproveUserRequest(BaseModel):
    """
    Schema for requesting user approval.

    Attributes:
        email (str): The email address of the user to be approved.
    """
    email: str


class UserResponse(BaseModel):
    """
    Schema for the response when querying user information.

    Attributes:
        id (uuid.UUID): The unique identifier of the user.
        email (str): The email address of the user.
        role (str): The role of the user in the system.
        approved (bool): Is user has been approved or not yet.
    """
    id: uuid.UUID
    email: str
    role: str
    approved: bool

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """
    Schema for the response when querying detailed user profile information.

    Attributes:
        id (uuid.UUID): The unique identifier of the user profile.
        user_id (uuid.UUID): The unique identifier of the user associated with this profile.
        restaurant_id (Optional[int]): The ID of the restaurant associated with the user profile, if applicable.
        restaurant_name (Optional[str]): The name of the restaurant associated with the user profile, if applicable.
        restaurant_reviews (Optional[str]): The link for reviews of the restaurant, if available.
        restaurant_photo (Optional[str]): A URL or reference to a photo of the restaurant, if available.
        telegram (Optional[str]): The Telegram handle of the user or restaurant, if provided.
        rating (Optional[str]): The rating of the restaurant, if available.
        restaurant_currency (Optional[str]): The currency used by the restaurant, if specified.
        tables_amount (int): The number of tables in the restaurant, if applicable.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    restaurant_id: Optional[int]
    restaurant_name: Optional[str]
    restaurant_reviews: Optional[str]
    restaurant_photo: Optional[str]
    telegram: Optional[str]
    rating: Optional[Decimal]
    restaurant_currency: Optional[str]
    tables_amount: int

    class Config:
        json_encoders = {
            Decimal: lambda v: f"{v:.1f}"  # Ensure one digit after the decimal point
        }


class RestaurantsResponse(BaseModel):
    """
    Schema for the response when querying restaurant profiles.

    Attributes:
        root (Dict[uuid.UUID, UserProfileResponse]): A dictionary where the keys are user IDs
            and the values are UserProfileResponse objects containing detailed information
            about the user's restaurant profile.
    """
    root: Dict[uuid.UUID, UserProfileResponse]


class UserProfileUpdate(BaseModel):
    """
    Schema for updating user profile information.

    Attributes:
        restaurant_name (Optional[str]): The name of the restaurant associated with the user profile, if applicable.
        restaurant_reviews (Optional[str]): The reviews of the restaurant, if available.
        restaurant_photo (Optional[str]): A URL or reference to a photo of the restaurant, if available.
        telegram (Optional[str]): The Telegram handle of the user or restaurant, if provided.
        rating (Optional[str]): The rating of the restaurant, if available.
        restaurant_currency (Optional[str]): The currency used by the restaurant, if specified.
        tables_amount (Optional[int]): The number of tables in the restaurant, if applicable.
    """
    restaurant_name: Optional[str] = None
    restaurant_reviews: Optional[str] = None
    restaurant_photo: Optional[str] = None
    telegram: Optional[str] = None
    rating: Optional[Decimal] = None
    restaurant_currency: Optional[str] = None
    tables_amount: Optional[int] = None

    @model_validator(mode='before')
    @classmethod
    def validate_rating(cls, values):
        rating = values.get('rating')
        if rating is not None:
            values['rating'] = round(rating, 1)
        return values


class PasswordResetRequest(BaseModel):
    """
    Schema for requesting a password reset.

    Attributes:
        email (EmailStr): The email address associated with the user account requesting a password reset.
    """
    email: EmailStr


class ChangePasswordRequest(BaseModel):

    email: str
    new_password: str


# class ChangePasswordRequest(BaseModel):
#     email: str
#     old_password: str
#     new_password: str
#
#     @model_validator(mode='before')
#     def check_passwords_not_equal(cls, values):
#         old_password = values.get('old_password')
#         new_password = values.get('new_password')
#         if old_password == new_password:
#             raise ValueError('New password must be different from the old password')
#         return values


class EmailRequest(BaseModel):
    """
    Schema for sending an email.

    Attributes:
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        message (str): The content of the email message.
    """
    recipient: str
    subject: str
    message: str


class DishResponse(BaseModel):
    id: int
    restaurant_id: int
    category_id: int
    name: str
    photo: Optional[str] = None
    description: str
    price: condecimal(max_digits=10, decimal_places=2)  # Adjust max_digits and decimal_places as needed
    extra: Optional[Dict] = None


class DishCreate(BaseModel):
    """
    Schema for creating a new dish.

    Attributes:
        email (str): The email address of the user.
        restaurant_id (int): The ID of the restaurant to which the dish belongs.
        category_id (int): The ID of the category to which the dish belongs.
        name (str): The name of the dish.
        description (str): A description of the dish.
        price (condecimal): The price of the dish.
        photo (Optional[str]): A URL or reference to a photo of the dish, if available.
        extra (Optional[dict]): Additional information or attributes related to the dish, if any.
    """
    email: str
    restaurant_id: int = Field(..., description="ID of the restaurant to which the dish belongs")
    category_id: int
    name: str
    description: str
    price: condecimal(max_digits=10, decimal_places=2)  # Adjust max_digits and decimal_places as needed
    photo: Optional[str] = None
    extra: Optional[dict] = None


class DishUpdate(BaseModel):
    """
    Schema for updating an existing dish.

    Attributes:
        email (str): The email address of the user.
        dish_id (int): The ID of the dish to update.
        restaurant_id (Optional[int]): The ID of the restaurant to which the dish belongs, if applicable.
        name (Optional[str]): The updated name of the dish, if applicable.
        description (Optional[str]): The updated description of the dish, if applicable.
        price (Optional[condecimal]): The updated price of the dish, if applicable.
        photo (Optional[str]): The updated URL or reference to a photo of the dish, if applicable.
        extra (Optional[dict]): Updated additional information or attributes related to the dish, if any.
    """
    email: str
    dish_id: int = Field(..., description="ID of the dish to update")
    restaurant_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[condecimal(max_digits=10, decimal_places=2)] = None  # Adjust max_digits and decimal_places as needed
    photo: Optional[str] = None
    extra: Optional[dict] = None


class DishDelete(BaseModel):
    """
    Schema for deleting a dish.

    Attributes:
        email (str): The email address of the user.
        dish_id (int): The ID of the dish to delete.
    """
    email: str
    dish_id: int = Field(..., description="ID of the dish to delete")



