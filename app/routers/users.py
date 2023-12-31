from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from .. import oauth2, schemas, database, models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get('/', response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Unable to fetch users')
    users_response = []
    for user in users:
        unread_count = (
            db.query(models.UnreadMessageCount).filter_by(sender_id=user.id, receiver_id=current_user.id).first()
        )
        users_response.append({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at,
            "online": user.online,
            "unread": unread_count.count if unread_count else 0,
        })

    return users_response
