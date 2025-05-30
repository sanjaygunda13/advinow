from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./diagnosis.db"

Base = declarative_base()

def create_db(url: str):
    engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    return SessionLocal
SessionLocal=create_db(SQLALCHEMY_DATABASE_URL)


@contextmanager
def create_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Commit changes if successful
    except Exception as e:
        session.rollback()  # Rollback changes in case of an exception
        raise e
    finally:
        session.close()