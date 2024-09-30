import asyncio
import logging
from sqlalchemy import event
from api.models.database.model import Edit, OccupiedSlot, User
from api.websocket.active_connections import notify_table_update
from sqlalchemy.orm import Session, joinedload

# Set up logging
logger = logging.getLogger("config.database_trigger")

# Helper function to get group_id from object
def get_group_id_from_object(obj):
    if isinstance(obj, Edit):
        return obj.group_id
    elif isinstance(obj, OccupiedSlot):
        return obj.edit.group_id
    elif isinstance(obj, User):
        return obj.group_id
    return None

# Helper function to run async task based on whether an event loop is running
def run_async(func, *args):
    try:
        # Check if an event loop is already running
        loop = asyncio.get_running_loop()
        # If we are in a running event loop, create a task
        loop.create_task(func(*args))
    except RuntimeError:
        # If no event loop is running, use asyncio.run()
        asyncio.run(func(*args))

# Event listener for Edit table
@event.listens_for(Edit, 'after_insert')
@event.listens_for(Edit, 'after_update')
@event.listens_for(Edit, 'after_delete')
def after_edit_update(mapper, connection, target):
    group_id = get_group_id_from_object(target)
    logger.info(f"Edit table updated. Group ID: {group_id}")
    if group_id:
        run_async(notify_table_update, group_id, 'EDIT')
    else:
        logger.warning("Edit table updated, but no group ID found.")

# Event listener for OccupiedSlot table
@event.listens_for(OccupiedSlot, 'after_insert')
@event.listens_for(OccupiedSlot, 'after_update')
@event.listens_for(OccupiedSlot, 'before_delete')
def after_occupied_slot_update(mapper, connection, target):
# Convert the connection into a SQLAlchemy session
    session = Session(bind=connection)

    # Eager load the edit relationship
    occupied_slot = session.query(OccupiedSlot)\
                           .options(joinedload(OccupiedSlot.edit))\
                           .filter_by(occupied_slot_id=target.occupied_slot_id)\
                           .first()

    group_id = get_group_id_from_object(occupied_slot)
    logger.info(f"OccupiedSlot table updated. Group ID: {group_id}")
    
    if group_id:
        run_async(notify_table_update, group_id, 'OCCUPIEDSLOT')
    else:
        logger.warning("OccupiedSlot table updated, but no group ID found.")
    
    session.close()

# Event listener for User table
@event.listens_for(User, 'after_insert')
@event.listens_for(User, 'after_update')
@event.listens_for(User, 'after_delete')
def after_user_update(mapper, connection, target):
    group_id = get_group_id_from_object(target)
    logger.info(f"User table updated. Group ID: {group_id}")
    if group_id:
        run_async(notify_table_update, group_id, 'USER')
    else:
        logger.warning("User table updated, but no group ID found.")
