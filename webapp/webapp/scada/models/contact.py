from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..sqlalchemy_setup import Base

from datetime import datetime


class Contact(Base):
    __tablename__ = 'contact'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    comment = Column(Text, nullable=False)
    datetime = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship back to Email
    emails = relationship("Email", back_populates="contact")

    def __repr__(self):
        return f"<Contact(name={self.name}, email={self.email})>"

