from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import TransitionCreate, VersionResponse
from app.models.user import User, RoleEnum
from app.api.dependencies import RoleChecker, get_current_user
from app.services.registry_service import RegistryService
from app.repositories.db_repository import RegistryDBRepository
from app.repositories.s3_repository import S3Repository

router = APIRouter(prefix="", tags=["Versions"])

def get_registry_service(db: Session = Depends(get_db)) -> RegistryService:
    return RegistryService(RegistryDBRepository(db), S3Repository())

@router.get("/models/{model_name}/versions")
def get_versions(model_name: str, stage: Optional[str] = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = RegistryDBRepository(db)
    model = repo.get_model_by_name(model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return repo.get_versions(model.id, stage)

@router.post("/models/{model_name}/versions", response_model=VersionResponse)
def upload_version(
    model_name: str,
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    dataset_reference: Optional[str] = Form(None),
    metrics: Optional[str] = Form(None),
    parameters: Optional[str] = Form(None),
    user: User = Depends(RoleChecker([RoleEnum.DEVELOPER])),
    svc: RegistryService = Depends(get_registry_service)
):
    return svc.create_version(model_name, user, file, source, dataset_reference, metrics, parameters)

@router.get("/versions/{version_id}")
def get_version_info(version_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = RegistryDBRepository(db)
    version = repo.get_version_by_id(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {
        "id": version.id, "version_number": version.version_number,
        "stage": version.current_stage, "source": version.source,
        "metrics": {m.key: m.value for m in version.metrics},
        "parameters": {p.key: p.value for p in version.parameters}
    }

@router.post("/versions/{version_id}/transitions")
def transition_stage(
    version_id: int, 
    data: TransitionCreate,
    user: User = Depends(RoleChecker([RoleEnum.DEVELOPER])), 
    svc: RegistryService = Depends(get_registry_service)
):
    return svc.transition_stage(version_id, user, data.target_stage, data.reason)

@router.get("/versions/{version_id}/transitions")
def get_transitions(version_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = RegistryDBRepository(db)
    return repo.get_transitions(version_id)

@router.get("/versions/{version_id}/download")
def download_model(version_id: int, user: User = Depends(get_current_user), svc: RegistryService = Depends(get_registry_service)):
    url = svc.get_download_url(version_id)
    return {"download_url": url}