from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash

from ..sqlalchemy_setup import Base

from datetime import datetime


class Facility(Base):
    __tablename__ = "facility"

    def __repr__(self):
        return f"<Facility(facility_id={self.facility_id})>"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth_entity.id"), nullable=False)
    facility_id = Column(String(255), nullable=False)

    # Establishing relationship to AuthEntity
    users = relationship(
        "AuthEntity", back_populates="facilities"
    )  # Allows access to facilities from the AuthEntity
