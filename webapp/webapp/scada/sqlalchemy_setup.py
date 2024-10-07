from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from django.conf import settings

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "webapp.settings.prod"

engine = create_engine(settings.DATABASE_URL_LOCAL, pool_recycle=3600)

# Create a scoped session
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(Session)

# Create a base class for declarative models
Base = declarative_base()
Base.query = db_session.query_property()


def get_dbsession():
    """
    Generator function to get a database session.
    Use this in views to ensure proper session handling.
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Initialize the database, creating all tables.
    Call this function when setting up your Django app.
    """
    # Import all modules here that might define models
    # from models import contact
    Base.metadata.create_all(bind=engine)
