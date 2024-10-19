from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash

from ..sqlalchemy_setup import Base

from datetime import datetime


class AuthEntity(Base):
    __tablename__ = "auth_entity"

    def __repr__(self):
        return f"<AuthEntity(username={self.username})>"

    id = Column(Integer, primary_key=True)
    username = Column(String(200), nullable=False)
    password = Column(String(500), nullable=False)  # hashed password
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    phone = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)

    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Establishing a relationship to Facility with a back reference
    facilities = relationship(
        "Facility", back_populates="users"
    )  # Access facilities from AuthEntity

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
