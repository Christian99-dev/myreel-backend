from typing import List
from sqlalchemy import Boolean, ForeignKey, String, Time, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base

Base = declarative_base()

class Slot(Base):
    __tablename__ = 'slot'

    slot_id:    Mapped[int]     = mapped_column(primary_key=True, autoincrement=True) 
    song_id:    Mapped[int]     = mapped_column(ForeignKey('song.song_id'), nullable=False)  
    start_time: Mapped[str]     = mapped_column(Time, nullable=False) 
    end_time:   Mapped[str]     = mapped_column(Time, nullable=False) 

    song:       Mapped["Song"]  = relationship(back_populates="slots")

class Song(Base):
    __tablename__ = 'song'

    song_id:    Mapped[int]             = mapped_column(primary_key=True, autoincrement=True)  
    name:       Mapped[str]             = mapped_column(String(255), nullable=False)  
    author:     Mapped[str]             = mapped_column(String(255), nullable=False)  
    times_used: Mapped[int]             = mapped_column(nullable=False)  
    cover_src:  Mapped[str]             = mapped_column(String(255), nullable=False)  
    audio_src:  Mapped[str]             = mapped_column(String(255), nullable=False) 

    slots:      Mapped[List["Slot"]]    = relationship(back_populates="song")
    edits:      Mapped[List["Edit"]]    = relationship(back_populates="song")

class Edit(Base):
    __tablename__ = 'edit'

    edit_id:        Mapped[int]                     = mapped_column(primary_key=True, autoincrement=True) 
    song_id:        Mapped[int]                     = mapped_column(ForeignKey('song.song_id'), nullable=False)  
    created_by:     Mapped[int]                     = mapped_column(ForeignKey('user.user_id'), nullable=False)  
    group_id:       Mapped[int]                     = mapped_column(ForeignKey('group.group_id'), nullable=False)  
    name:           Mapped[str]                     = mapped_column(String(255), nullable=False) 
    isLive:         Mapped[bool]                    = mapped_column(Boolean, nullable=False)  

    song:           Mapped["Song"]                  = relationship(back_populates="edits")
    group:          Mapped["Group"]                 = relationship(back_populates="edits")
    creator:        Mapped["User"]                  = relationship(back_populates="edits")
    occupied_slots: Mapped[List["OccupiedSlot"]]    = relationship(back_populates="edit")

class Group(Base):
    __tablename__ = 'group'

    group_id:       Mapped[int]                 = mapped_column(primary_key=True, autoincrement=True)  
    name:           Mapped[str]                 = mapped_column(String(255), nullable=False) 

    users:          Mapped[List["User"]]        = relationship(back_populates="group")
    edits:          Mapped[List["Edit"]]        = relationship(back_populates="group")
    invitations:    Mapped[List["Invitation"]]  = relationship(back_populates="group")

class Invitation(Base):
    __tablename__ = 'invitation'

    invitation_id:  Mapped[int]     = mapped_column(primary_key=True, autoincrement=True) 
    group_id:       Mapped[int]     = mapped_column(ForeignKey('group.group_id'), nullable=False)  
    token:          Mapped[str]     = mapped_column(String(255), nullable=False)  
    email:          Mapped[str]     = mapped_column(String(255), nullable=False) 
    created_at:     Mapped[str]     = mapped_column(DateTime, nullable=False) 
    expires_at:     Mapped[str]     = mapped_column(DateTime, nullable=False)  

    group:          Mapped["Group"] = relationship(back_populates="invitations")

class User(Base):
    __tablename__ = 'user'

    user_id:        Mapped[int]                     = mapped_column(primary_key=True, autoincrement=True) 
    group_id:       Mapped[int]                     = mapped_column(ForeignKey('group.group_id'), nullable=False) 
    role:           Mapped[str]                     = mapped_column(String(255), nullable=False) 
    name:           Mapped[str]                     = mapped_column(String(255), nullable=False) 
    email:          Mapped[str]                     = mapped_column(String(255), nullable=False, unique=True)  

    group:          Mapped["Group"]                 = relationship(back_populates="users")
    edits:          Mapped[List["Edit"]]            = relationship(back_populates="creator")
    login_requests: Mapped[List["LoginRequest"]]    = relationship(back_populates="user")
    occupied_slots: Mapped[List["OccupiedSlot"]]    = relationship(back_populates="user")

class LoginRequest(Base):
    __tablename__ = 'login_request'

    user_id:    Mapped[int]     = mapped_column(ForeignKey('user.user_id'), primary_key=True)  
    pin:        Mapped[str]     = mapped_column(String(255), nullable=False)  
    created_at: Mapped[str]     = mapped_column(DateTime, nullable=False) 
    expires_at: Mapped[str]     = mapped_column(DateTime, nullable=False) 

    user:       Mapped["User"]  = relationship(back_populates="login_requests")

class OccupiedSlot(Base):
    __tablename__ = 'occupied_slot'

    user_id:    Mapped[int]     = mapped_column(ForeignKey('user.user_id'), primary_key=True) 
    slot_id:    Mapped[int]     = mapped_column(ForeignKey('slot.slot_id'), primary_key=True) 
    edit_id:    Mapped[int]     = mapped_column(ForeignKey('edit.edit_id'), primary_key=True) 

    user:       Mapped["User"]  = relationship(back_populates="occupied_slots")
    slot:       Mapped["Slot"]  = relationship(back_populates="occupied_slots")
    edit:       Mapped["Edit"]  = relationship(back_populates="occupied_slots")
