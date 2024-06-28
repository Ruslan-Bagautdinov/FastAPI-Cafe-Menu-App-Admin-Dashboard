from pydantic import BaseModel, EmailStr, RootModel, field_validator
from typing import Optional, Dict, Any
import uuid


class UserRegister(BaseModel):
    """
    Schema for user registration.

    Attributes:
        email (EmailStr): The email address of the user.
        password (str): The password for the user account.
    """
    email: EmailStr
    password: str


class UserCreate(UserRegister):
    """
    Schema for creating a new user, extending from UserRegister.

    Attributes:
        email (EmailStr): The email address of the user (inherited from UserRegister).
        password (str): The password for the user account (inherited from UserRegister).
        role (str): The role of the user, can be 'superuser' or 'restaurant'.
    """
    role: str

    @field_validator('role')
    def validate_role(cls, value):
        if value not in ['superuser', 'restaurant']:
            raise ValueError("Role must be 'superuser' or 'restaurant'")
        return value


class UserLogin(UserRegister):
    """
    Schema for user login, extending from UserRegister.

    Attributes:
        email (EmailStr): The email address of the user (inherited from UserRegister).
        password (str): The password for the user account (inherited from UserRegister).
    """
    pass


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
    restaurant_photo: Optional[str]
    telegram: Optional[str]
    rating: Optional[str]
    restaurant_currency: Optional[str]
    tables_amount: int


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
        restaurant_photo (Optional[str]): A URL or reference to a photo of the restaurant, if available.
        telegram (Optional[str]): The Telegram handle of the user or restaurant, if provided.
        rating (Optional[str]): The rating of the restaurant, if available.
        restaurant_currency (Optional[str]): The currency used by the restaurant, if specified.
        tables_amount (Optional[int]): The number of tables in the restaurant, if applicable.
    """
    restaurant_name: Optional[str] = None
    restaurant_photo: Optional[str] = None
    telegram: Optional[str] = None
    rating: Optional[str] = None
    restaurant_currency: Optional[str] = None
    tables_amount: Optional[int] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class EmailRequest(BaseModel):
    recipient: str
    subject: str
    message: str

