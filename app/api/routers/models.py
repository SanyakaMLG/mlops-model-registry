from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import ModelCreate
from app.models.user import RoleEnum
from app.api.dependencies import RoleChecker, get_current_user
from app.repositories.db_repository import RegistryDBRepository

router = APIRouter(prefix="/models", tags=["Models"])

@router.post("")
def create_model(data: ModelCreate, db: Session = Depends(get_db), user=Depends(RoleChecker([RoleEnum.DEVELOPER]))):
    repo = RegistryDBRepository(db)
    if repo.get_model_by_name(data.name):
        raise HTTPException(status_code=400, detail="Model already exists")
    return repo.create_model(data.name, data.description)

@router.get("")
def get_models(limit: int = 100, offset: int = 0, db: Session = Depends(get_db), user=Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.DEVELOPER]))):
    repo = RegistryDBRepository(db)
    return repo.get_models(limit, offset)

@router.get("/{model_name}")
def get_model(model_name: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = RegistryDBRepository(db)
    model = repo.get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model