from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine('sqlite:///:memory:', echo=True)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
