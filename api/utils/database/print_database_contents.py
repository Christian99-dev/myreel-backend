from sqlalchemy.orm import Session
from typing import Dict
from sqlalchemy import select
from api.models.database import model
from tabulate import tabulate

def print_database_contents(database_session: Session, show_tables: Dict[str, bool]):
    def filter_instance_state(data):
        return {key: value for key, value in data.items() if key != '_sa_instance_state'}

    if show_tables.get('Slot', False):
        print("Slot Table:")
        slots = database_session.execute(select(model.Slot)).scalars().all()
        slot_data = [filter_instance_state(instance.__dict__) for instance in slots]
        print(tabulate(slot_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('Song', False):
        print("Song Table:")
        songs = database_session.execute(select(model.Song)).scalars().all()
        song_data = [filter_instance_state(instance.__dict__) for instance in songs]
        print(tabulate(song_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('Edit', False):
        print("Edit Table:")
        edits = database_session.execute(select(model.Edit)).scalars().all()
        edit_data = [filter_instance_state(instance.__dict__) for instance in edits]
        print(tabulate(edit_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('Group', False):
        print("Group Table:")
        groups = database_session.execute(select(model.Group)).scalars().all()
        group_data = [filter_instance_state(instance.__dict__) for instance in groups]
        print(tabulate(group_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('Invitation', False):
        print("Invitation Table:")
        invitations = database_session.execute(select(model.Invitation)).scalars().all()
        invitation_data = [filter_instance_state(instance.__dict__) for instance in invitations]
        print(tabulate(invitation_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('User', False):
        print("User Table:")
        users = database_session.execute(select(model.User)).scalars().all()
        user_data = [filter_instance_state(instance.__dict__) for instance in users]
        print(tabulate(user_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('LoginRequest', False):
        print("LoginRequest Table:")
        login_requests = database_session.execute(select(model.LoginRequest)).scalars().all()
        login_request_data = [filter_instance_state(instance.__dict__) for instance in login_requests]
        print(tabulate(login_request_data, headers="keys", tablefmt="grid"))
    
    if show_tables.get('OccupiedSlot', False):
        print("OccupiedSlot Table:")
        occupied_slots = database_session.execute(select(model.OccupiedSlot)).scalars().all()
        occupied_slot_data = [filter_instance_state(instance.__dict__) for instance in occupied_slots]
        print(tabulate(occupied_slot_data, headers="keys", tablefmt="grid"))