from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="owner")
    permissions = relationship("TaskPermission", back_populates="user")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Integer, index=True, nullable=False)
    description = Column(String)
    create_at = Column(TIMESTAMP, server_default='NOW()')
    update_at = Column(TIMESTAMP, server_default='NOW()')

    owner = relationship("User", back_populates="tasks")
    permissions = relationship("TaskPermission", back_populates="task")


class TaskPermission(Base):
    __tablename__ = "task_permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))

    can_read = Column(Boolean, default=False)
    can_update = Column(Boolean, default=False)

    user = relationship("User", back_populates="permissions")
    task = relationship("Task", back_populates="permissions")
