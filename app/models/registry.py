import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class StageEnum(str, enum.Enum):
    NONE = "NONE"
    STAGE = "STAGE"
    PROD = "PROD"
    AB = "AB"
    ARCHIVED = "ARCHIVED"

class RegisteredModel(Base):
    __tablename__ = "registered_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("registered_models.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False) # FK на пользователя
    source = Column(String, nullable=True)
    dataset_reference = Column(String, nullable=True)
    current_stage = Column(Enum(StageEnum), default=StageEnum.NONE)
    s3_artifact_uri = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("RegisteredModel", back_populates="versions")
    metrics = relationship("ModelMetric", back_populates="version", cascade="all, delete-orphan")
    parameters = relationship("ModelParameter", back_populates="version", cascade="all, delete-orphan")

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    
    version = relationship("ModelVersion", back_populates="metrics")

class ModelParameter(Base):
    __tablename__ = "model_parameters"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    
    version = relationship("ModelVersion", back_populates="parameters")

class StateTransition(Base):
    __tablename__ = "state_transitions"
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False)
    from_stage = Column(String, nullable=False)
    to_stage = Column(String, nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False) # FK на пользователя
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)