from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from urllib.parse import parse_qs

from api.services.database.group import is_group_member
from api.sessions.database import get_database_session
from api.utils.jwt.jwt import read_jwt
from api.websocket.active_connections import active_connections


router = APIRouter(prefix="/ws")

@router.websocket("/updates/{group_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    group_id: str,
    database_session: Session = Depends(get_database_session)
):
    """
    WebSocket endpoint for handling group-specific updates.
    The client must authenticate with a JWT and provide a valid group_id.
    """
    try:
        # Query-Parameter parsen
        query_params = parse_qs(websocket.scope["query_string"].decode())
        token_list = query_params.get("token")
        if not token_list:
            await websocket.close(code=1008)  # Unauthorized access
            return
        authorization = token_list[0]

        # Step 1: Verify JWT and obtain user_id
        user_id = read_jwt(authorization.replace("Bearer ", ""))

        # Step 2: Verify the user is part of the group
        if not is_group_member(user_id, group_id, database_session):
            await websocket.close(code=4001)  # Unauthorized access
            return

        # Step 3: Accept WebSocket connection
        await websocket.accept()

        # Add the WebSocket connection to the group
        if group_id not in active_connections:
            active_connections[group_id] = []
        active_connections[group_id].append(websocket)

        # Keep the connection alive to receive updates
        while True:
            try:
                await websocket.receive_text()  # Placeholder for receiving messages (if necessary)
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        # Handle disconnection
        if group_id in active_connections:
            if websocket in active_connections[group_id]:
                active_connections[group_id].remove(websocket)
            if not active_connections[group_id]:
                del active_connections[group_id]

    finally:
        # Clean up connection if necessary
        if group_id in active_connections and websocket in active_connections[group_id]:
            active_connections[group_id].remove(websocket)
