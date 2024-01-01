from typing import Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from . import schemas, database, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 10
BLACKLIST = set()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException,db:Session) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id: str = payload.get("user_id")
        if user_id is None or token in BLACKLIST:
            db.query(models.User).filter(models.User.id == str(user_id)).update({'online': False})
            db.commit()
            raise credentials_exception
        token_data = schemas.TokenData(user_id=str(user_id))
    except JWTError:
        raise credentials_exception
    return token_data

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> Type[models.User] | None:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    token_data = verify_access_token(token=token, credentials_exception=credentials_exception,db = db)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    return user

# Add a route to handle logout
def logout(token: str = Depends(oauth2_scheme)):
    BLACKLIST.add(token)
    return {"message": "Logout successful"}
