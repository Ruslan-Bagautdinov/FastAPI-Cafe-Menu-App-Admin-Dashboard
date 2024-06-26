from sqlalchemy import ForeignKey, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import UUID
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
    restaurant_name: Mapped[str] = mapped_column(index=True, nullable=True)
    restaurant_photo: Mapped[str] = mapped_column(index=True, nullable=True)
    telegram: Mapped[str] = mapped_column(index=True, nullable=True)
    rating: Mapped[str] = mapped_column(index=True, nullable=True)
    restaurant_currency: Mapped[str] = mapped_column(index=True, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="profile")
