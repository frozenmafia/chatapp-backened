from fastapi import APIRouter, status, Depends, HTTPException, WebSocket, WebSocketDisconnect, WebSocketException
from starlette.websockets import WebSocketState

from .. import database, schemas, models, utils, oauth2
from typing import List, Dict
# from ..webconn.webconn import connection_manager

from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

connected_clients: Dict[str, WebSocket] = {}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    exists = db.query(models.User).filter(models.User.email == user.email).first()
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User with this email already exists')

    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/logout/{user_id}", status_code=status.HTTP_200_OK)
async def logout_user(user_id: int, db: Session = Depends(database.get_db)):
    exists = db.query(models.User).filter(models.User.id == user_id).first()

    if exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User not found')

    db.query(models.User).filter(models.User.id == user_id).update({'online': False})
    db.commit()
    await disconnect_user(str(user_id))


@router.post("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(database.get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id : {user_id} was not found')
    return user


@router.websocket("/ws/connect/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(database.get_db)):
    await  websocket.accept()
    if user_id not in connected_clients:
        connected_clients[str(user_id)] = websocket
        await broadcast("#Connected#")

    try:
        while True:
            data = await websocket.receive_text()
            print(connected_clients)
            x = data.split(":")
            receiver_id = x[-1]
            content = x[0]

            await send_message(str(user_id), receiver_id, content, db)
    except WebSocketDisconnect as e:
        print(f"Client {websocket.client.host} disconnected: {e}")


async def send_message(user: str, receiver: str, content, db):
    if db is not None:
        save_message(user, receiver, content, db)
    if user in connected_clients:
        await connected_clients[user].send_text(f"{content}")
    else:
        # Handle the case where the user is not connected
        # (e.g., log a warning or take appropriate action)
        print(f"User {user} not connected")

    if receiver in connected_clients:
        await connected_clients[receiver].send_text(f"{content}")
    else:
        # Handle the case where the receiver is not connected
        # (e.g., log a warning or take appropriate action)
        print(f"Receiver {receiver} not connected")


def save_message(user, receiver, content, db: Session):
    message = models.Message(sender_id=user, receiver_id=receiver, type="txtMsg", content=content)
    db.add(message)

    # db.commit()
    print(f'sender is {user} and receiver is {receiver}')
    unread_count = db.query(models.UnreadMessageCount).filter_by(sender_id=user, receiver_id=receiver).first()

    if unread_count:
        db.query(models.UnreadMessageCount).filter_by(sender_id=user, receiver_id=receiver).update(
            {"count": unread_count.count + 1})
    else:
        unread_count = models.UnreadMessageCount(sender_id=user, receiver_id=receiver, count=1)
        db.add(unread_count)

    # db.refresh(unread_count)
    # print("count is ", unread_count.count)
    db.commit()


async def broadcast(message):
    print("broadcasting")
    for connection in connected_clients.values():
        try:
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.send_text(message)
        except Exception:
            print("Error while broadcasting")


async def disconnect_user(user_id: str):
    try:
        # Close the WebSocket connection
        await connected_clients[user_id].close()
        # Remove the user from the connected_clients dictionary
        del connected_clients[user_id]
        await broadcast("#Connected#")
    except KeyError:
        # Handle the case where the user is not in the dictionary
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
