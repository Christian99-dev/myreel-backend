import logging
logger = logging.getLogger("websocket.active_connections")

active_connections = {}

async def notify_table_update(group_id: str, table_name: str):
    """
    Notify all connected WebSocket clients in a specific group about an update to a table.
    """
    
    logger.info(f"group_id {group_id}, table_name {table_name}")
    
    if group_id in active_connections:
        for connection in active_connections[group_id]:
            await connection.send_text(f"{table_name}")