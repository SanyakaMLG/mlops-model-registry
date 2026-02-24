from typing import Optional, Dict
from pydantic import BaseModel, Field, EmailStr
from app.models.user import RoleEnum
from app.models.registry import StageEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ModelCreate(BaseModel):
    name: str = Field(..., example="recsys_main_feed")
    description: Optional[str] = Field(None, example="Модель ранжирования")

class TransitionCreate(BaseModel):
    target_stage: StageEnum
    reason: Optional[str] = Field(None, example="Пройдены A/B тесты")

class VersionResponse(BaseModel):
    id: int
    model_id: int
    version_number: int
    current_stage: StageEnum
    s3_artifact_uri: str
    
    class Config:
        from_attributes = True