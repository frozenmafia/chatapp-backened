from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL_DEV = 'postgresql://postgres:123qwe123qwe@localhost/chatapp4'
SQLALCHEMY_DATABASE_URL = 'postgresql://shivajay295:9DjAZuiMdb7V@ep-cold-mountain-40940784.ap-southeast-1.aws.neon.tech/chatapp4?sslmode=require'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

