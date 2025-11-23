"""
Database schema models using SQLAlchemy ORM.
"""
from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from context.src.database import Base


class Project(Base):
    """Projects table - stores high-level project information"""
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    goal = Column(Text, nullable=False)
    constraints = Column(JSON, nullable=False, default=dict)
    user_preferences = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agent_history = relationship("AgentHistory", back_populates="project", cascade="all, delete-orphan")
    deployment_info = relationship("DeploymentInfo", back_populates="project", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_project_user_created', 'user_id', 'created_at'),
    )


class Task(Base):
    """Tasks table - stores individual tasks in the execution graph"""
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False, index=True)
    agent = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    depends_on = Column(JSON, nullable=False, default=list)  # Array of task_ids
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")

    __table_args__ = (
        Index('idx_task_project_status', 'project_id', 'status'),
    )


class AgentHistory(Base):
    """Agent history table - stores all agent responses"""
    __tablename__ = "agent_history"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False, index=True)
    task_id = Column(String, nullable=False, index=True)
    agent = Column(String, nullable=False)
    status = Column(String, nullable=False)
    response_json = Column(JSON, nullable=False)  # Full AgentResponse as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="agent_history")

    __table_args__ = (
        Index('idx_history_project_created', 'project_id', 'created_at'),
        Index('idx_history_task', 'task_id'),
    )


class DeploymentInfo(Base):
    """Deployment info table - stores deployment details"""
    __tablename__ = "deployment_info"

    project_id = Column(String, ForeignKey("projects.project_id"), primary_key=True)
    app_url = Column(String, nullable=True)
    deployment_id = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="deployment_info")
