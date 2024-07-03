from sqlalchemy import (Column,
                        Boolean,
                        Integer,
                        ForeignKey,
                        DateTime,
                        JSON,
                        String,
                        Numeric,
                        Enum)

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

# own import
from app.database.postgre_db import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String, index=True)
    approved: Mapped[bool] = mapped_column(Boolean, index=True, default=False)

    @validates('role')
    def validate_role(self, key, role):
        if role not in ['superuser', 'restaurant']:
            raise ValueError("Role must be 'superuser' or 'restaurant'")
        return role

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user")


class UserProfile(Base):

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=True)
    restaurant_name: Mapped[str] = mapped_column(index=True, nullable=True)
    restaurant_reviews: Mapped[str] = mapped_column(index=True, nullable=True)
    restaurant_photo: Mapped[str] = mapped_column(index=True, nullable=True)
    telegram: Mapped[str] = mapped_column(index=True, nullable=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(2, 1), nullable=True)
    restaurant_currency: Mapped[str] = mapped_column(index=True, nullable=True)
    tables_amount: Mapped[int] = mapped_column(nullable=False)

    user: Mapped[User] = relationship("User", back_populates="profile")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="profiles", cascade="all, delete")


class ResetToken(Base):

    __tablename__ = "reset_tokens"

    token = Column(String, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    expiry_time = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    user = relationship("User", backref="reset_tokens")


class Restaurant(Base):

    __tablename__ = 'restaurants'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    photo: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(2, 1), nullable=False)  # Use Decimal for type annotation
    currency: Mapped[str] = mapped_column(nullable=False, default='USD')
    tables_amount: Mapped[int] = mapped_column(nullable=False)

    dishes: Mapped[list['Dish']] = relationship('Dish', back_populates='restaurant', cascade='all, delete-orphan')
    profiles: Mapped[list["UserProfile"]] = relationship("UserProfile", back_populates="restaurant", cascade='all, delete-orphan')


class Category(Base):

    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    dishes: Mapped[list['Dish']] = relationship('Dish', back_populates='category')


class Dish(Base):

    __tablename__ = 'dishes'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurants.id', ondelete='CASCADE'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    name: Mapped[str] = mapped_column(nullable=False)
    photo: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    extra: Mapped[dict] = mapped_column(JSON)

    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='dishes')
    category: Mapped['Category'] = relationship('Category', back_populates='dishes')


class Basket(Base):

    __tablename__ = 'baskets'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    table_id: Mapped[int] = mapped_column(Integer, nullable=False)
    order_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    order_items: Mapped[dict] = mapped_column(JSONB, nullable=True)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False, default='USD')
    status: Mapped[str] = mapped_column(String, nullable=True)
    waiter: Mapped[str] = mapped_column(String, nullable=True)


class WaiterCall(Base):

    __tablename__ = 'waiter_calls'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    table_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

