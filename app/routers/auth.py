from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, models, utils, oauth2, schemas

router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.LoginResponse)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid credentials')
    token_data = {"user_id": user.id}
    access_token = oauth2.create_access_token(token_data)
    db.query(models.User).filter(models.User.email == user_credentials.username).update({"online": True})
    db.commit()
    login_response = schemas.LoginResponse(user_id=user.id, username=user.name, email=user.email, access_token=access_token,
                                           token_type="bearer")
    return login_response

