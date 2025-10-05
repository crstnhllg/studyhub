from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
    Enum
    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String(250), index=True, unique=True, nullable=False)
    username = Column(String(250), index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    sessions = relationship('StudySession', back_populates='creator', cascade='all, delete')
    memberships = relationship('Membership', back_populates='user', cascade='all, delete')



class StudyGroup(Base):
    __tablename__ = 'study_groups'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(250), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)

    subjects = relationship('Subject', back_populates='group', cascade='all, delete')
    memberships = relationship('Membership', back_populates='group', cascade='all, delete')



class Membership(Base):
    __tablename__ = 'memberships'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('study_groups.id'), primary_key=True, nullable=False)
    role = Column(Enum('Member', 'Admin', 'Creator', name='role_name'), default='Member', nullable=False)
    joined_at = Column(DateTime, default=datetime.now(timezone.utc))

    group = relationship('StudyGroup', back_populates='memberships')
    user = relationship('User', back_populates='memberships')




class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(250), nullable=False)
    group_id = Column(Integer, ForeignKey('study_groups.id', ondelete='CASCADE'), index=True, nullable=False)

    __table_args__ = (
        UniqueConstraint('group_id', 'name', name='uq_group_subject_name'),
    )

    sessions = relationship('StudySession', back_populates='subject', cascade='all, delete')
    group = relationship('StudyGroup', back_populates='subjects')



class StudySession(Base):
    __tablename__ = 'study_sessions'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(250), nullable=False)
    description = Column(Text)
    date_time = Column(DateTime, index=True, nullable=False)
    duration = Column(Integer, nullable=False)
    status = Column(Enum('Scheduled', 'Completed', 'In Progress', 'Cancelled', name='session_status'),
                    default='Scheduled', nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), index=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        CheckConstraint('duration > 0', name='duration_range'),
    )

    creator = relationship('User', back_populates='sessions')
    subject = relationship('Subject', back_populates='sessions')