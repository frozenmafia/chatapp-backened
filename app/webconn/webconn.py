from typing import Dict
from fastapi import WebSocket, WebSocketException
from starlette.websockets import WebSocketState


class WebConn:
    def __init__(self):
        self.connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket
        print(self.connections)
        await self.broadcast(f'#Connected#')

    async def disconnect(self, user_id: int):
        if user_id in self.connections:
            del self.connections[user_id]
        await self.broadcast(f'#Connected#')

    async def send_message(self, user_id: int, message: str):
        print(f'sending message to {user_id}')
        print(self.connections)
        if user_id in self.connections:
            await self.connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.connections.values():
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(message)
            except WebSocketException:
                # Handle the closed connection gracefully (e.g., log the error)
                print("Error found")


connection_manager = WebConn()
