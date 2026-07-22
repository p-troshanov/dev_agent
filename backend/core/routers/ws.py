# backend/core/routers/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from backend.core.config import JWT_SECRET, JWT_ALGORITHM
from backend.core.state import state

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/frontend")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    if not token:
        await websocket.close(code=1008)
        return
    
    try:
        # Декодируем JWT токен для получения ID пользователя
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            await websocket.close(code=1008)
            return
        user_id = int(user_id_str)
    except JWTError:
        await websocket.close(code=1008)
        return

    # Принимаем соединение и добавляем в стейт
    await websocket.accept()
    state.add_connection(user_id, websocket)
    
    try:
        while True:
            # Держим соединение активным
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        state.remove_connection(user_id, websocket)
    except Exception:
        state.remove_connection(user_id, websocket)
