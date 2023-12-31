from fastapi import APIRouter, Depends
from .. import database, oauth2, schemas, models
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .user import send_message

router = APIRouter(
    prefix="/messages",
    tags=["User"]
)


@router.get("/fetch_all", response_model=List[schemas.Message])
def fetch_all(current_user: models.User = Depends(oauth2.get_current_user), db: Session = Depends(database.get_db)):
    messages = db.query(models.Message).filter(
        or_(models.Message.sender_id == current_user.id, models.Message.receiver_id == current_user.id)).order_by(models.Message.id).all()
    return messages


@router.post("/update_count")
async def update_count(count: schemas.UpdateCount, current_user: models.User = Depends(oauth2.get_current_user),
                       db: Session = Depends(database.get_db)):
    print("---------------------------------")
    update_count = models.UnreadMessageCount(**count.dict())
    print(update_count)
    db.add(update_count)

    # Commit the session to persist the instance
    db.commit()
    db.query(models.UnreadMessageCount).filter_by(receiver_id=update_count.receiver_id,sender_id = update_count.sender_id).update({"count":update_count.count})

    db.commit()
    await send_message(update_count.sender_id, update_count.receiver_id, f'Update message',db=None)
    db.refresh(update_count)

