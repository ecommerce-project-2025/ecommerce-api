from sqlmodel import Session, create_engine
from contextlib import contextmanager
from core.config import dbSettings

engine = create_engine(dbSettings.database_url)

@contextmanager
def getSession():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
