from typing import List
from sqlalchemy import Boolean, ForeignKey, String, Time, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base

Base = declarative_base()

class Slot(Base):
    __tablename__ = 'slot'

    slot_id:    Mapped[int]                 = mapped_column(primary_key=True, autoincrement=True)
    song_id:    Mapped[int]                 = mapped_column(ForeignKey('song.song_id'), nullable=False)
    start_time: Mapped[str]                 = mapped_column(Time, nullable=False)
    end_time:   Mapped[str]                 = mapped_column(Time, nullable=False)

    song:           Mapped["Song"]          = relationship("Song", back_populates="slot_list")
    occupied_slots: Mapped["OccupiedSlot"]  = relationship("OccupiedSlot", back_populates="slot")

class Song(Base):
    __tablename__ = 'song'

    song_id:    Mapped[int]             = mapped_column(primary_key=True, autoincrement=True)
    name:       Mapped[str]             = mapped_column(String(255), nullable=False)
    author:     Mapped[str]             = mapped_column(String(255), nullable=False)
    times_used: Mapped[int]             = mapped_column(nullable=False)
    cover_src:  Mapped[str]             = mapped_column(String(255), nullable=False)
    audio_src:  Mapped[str]             = mapped_column(String(255), nullable=False)

    slot_list:  Mapped[List["Slot"]]    = relationship("Slot", back_populates="song")
    edit_list:  Mapped[List["Edit"]]    = relationship("Edit", back_populates="song")

class Edit(Base):
    __tablename__ = 'edit'

    edit_id:        Mapped[int]                     = mapped_column(primary_key=True, autoincrement=True)
    song_id:        Mapped[int]                     = mapped_column(ForeignKey('song.song_id'), nullable=False)
    created_by:     Mapped[int]                     = mapped_column(ForeignKey('user.user_id'), nullable=False)
    group_id:       Mapped[str]                     = mapped_column(ForeignKey('group.group_id'), nullable=False)
    name:           Mapped[str]                     = mapped_column(String(255), nullable=False)
    isLive:         Mapped[bool]                    = mapped_column(Boolean, nullable=False)
    video_src:      Mapped[str]                     = mapped_column(String(255), nullable=False)

    song:           Mapped["Song"]                  = relationship("Song", back_populates="edit_list")
    group:          Mapped["Group"]                 = relationship("Group", back_populates="edit_list")
    creator:        Mapped["User"]                  = relationship("User", back_populates="edit_list")
    occupied_slots: Mapped[List["OccupiedSlot"]]    = relationship("OccupiedSlot", back_populates="edit")

class Group(Base):
    __tablename__ = 'group'

    group_id:           Mapped[str]                 = mapped_column(primary_key=True)
    name:               Mapped[str]                 = mapped_column(String(255), nullable=False)

    user_list:          Mapped[List["User"]]        = relationship("User", back_populates="group")
    edit_list:          Mapped[List["Edit"]]        = relationship("Edit", back_populates="group")
    invitation_list:    Mapped[List["Invitation"]]  = relationship("Invitation", back_populates="group")

class Invitation(Base):
    __tablename__ = 'invitation'

    invitation_id:  Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    group_id:       Mapped[str]     = mapped_column(ForeignKey('group.group_id'), nullable=False)
    token:          Mapped[str]     = mapped_column(String(255), nullable=False)
    email:          Mapped[str]     = mapped_column(String(255), nullable=False)
    created_at:     Mapped[str]     = mapped_column(DateTime, nullable=False)
    expires_at:     Mapped[str]     = mapped_column(DateTime, nullable=False)

    group:          Mapped["Group"] = relationship("Group", back_populates="invitation_list")

class User(Base):
    __tablename__ = 'user'

    user_id:            Mapped[int]                  = mapped_column(primary_key=True, autoincrement=True)
    group_id:           Mapped[str]                  = mapped_column(ForeignKey('group.group_id'), nullable=False)
    role:               Mapped[str]                  = mapped_column(String(255), nullable=False)
    name:               Mapped[str]                  = mapped_column(String(255), nullable=False)
    email:              Mapped[str]                  = mapped_column(String(255), nullable=False, unique=True)

    group:              Mapped["Group"]              = relationship("Group", back_populates="user_list")
    edit_list:          Mapped[List["Edit"]]         = relationship("Edit", back_populates="creator")
    login_request_list: Mapped[List["LoginRequest"]] = relationship("LoginRequest", back_populates="user")
    occupied_slot_list: Mapped[List["OccupiedSlot"]] = relationship("OccupiedSlot", back_populates="user")

class LoginRequest(Base):
    __tablename__ = 'login_request'

    user_id:    Mapped[int]     = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    pin:        Mapped[str]     = mapped_column(String(255), nullable=False)
    created_at: Mapped[str]     = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[str]     = mapped_column(DateTime, nullable=False)

    user:       Mapped["User"]  = relationship("User", back_populates="login_request_list")

class OccupiedSlot(Base):
    __tablename__ = 'occupied_slot'

    user_id:    Mapped[int]     = mapped_column(ForeignKey('user.user_id'), primary_key=True)
    slot_id:    Mapped[int]     = mapped_column(ForeignKey('slot.slot_id'), primary_key=True)
    edit_id:    Mapped[int]     = mapped_column(ForeignKey('edit.edit_id'), primary_key=True)
    video_src:  Mapped[str]     = mapped_column(String(255), nullable=False)

    user:       Mapped["User"]  = relationship("User", back_populates="occupied_slot_list")
    slot:       Mapped["Slot"]  = relationship("Slot", back_populates="occupied_slots")
    edit:       Mapped["Edit"]  = relationship("Edit", back_populates="occupied_slots")
