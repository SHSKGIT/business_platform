from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash

from ..sqlalchemy_setup import Base

from datetime import datetime


class AuthEntity(Base):
    __tablename__ = "auth_entity"

    def __repr__(self):
        return f"<AuthEntity(username={self.username})>"

    id = Column(Integer, primary_key=True)
    username = Column(String(200), unique=True, nullable=False)
    password = Column(String(500), nullable=False)  # hashed password
    email = Column(String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
