from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..sqlalchemy_setup import Base

from datetime import datetime


class Email(Base):
    __tablename__ = "email"

    # name = models.CharField(max_length=200)
    # email = models.CharField(max_length=200)
    # comment = models.TextField(blank=False, null=False)
    # date = models.DateTimeField(default=datetime.now(), blank=False)

    id = Column(Integer, primary_key=True)
    subject = Column(String(200), nullable=True)
    sender = Column(String(200), nullable=False)
    recipient = Column(String(200), nullable=False)
    cc = Column(String(500), nullable=True)
    is_sent = Column(Boolean, nullable=False, default=True)
    datetime = Column(DateTime, default=datetime.now, nullable=False)

    # Foreign key that references the Contact table
    contact_id = Column(Integer, ForeignKey("contact.id"))

    # Relationship to Contact
    contact = relationship("Contact", back_populates="emails")

    # Foreign key that references the Subscribe table
    subscribe_id = Column(Integer, ForeignKey("subscribe.id"))

    # Relationship to Subscribe
    subscribe = relationship("Subscribe", back_populates="emails")

    def __repr__(self):
        return f"<Email(sender={self.sender}, recipient={self.recipient}, is_sent={self.is_sent})>"
