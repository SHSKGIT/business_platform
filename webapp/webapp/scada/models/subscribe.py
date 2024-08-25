from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..sqlalchemy_setup import Base

from datetime import datetime


class Subscribe(Base):
    __tablename__ = "subscribe"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    phone = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    datetime = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship back to Email
    emails = relationship("Email", back_populates="subscribe")

    def __repr__(self):
        return f"<Contact(first_name={self.first_name}, last_name={self.last_name}, company={self.company}, email={self.email})>"
