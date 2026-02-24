import json
from fastapi import HTTPException
from app.models.user import User
from app.repositories.db_repository import RegistryDBRepository
from app.repositories.s3_repository import S3Repository

class RegistryService:
    def __init__(self, db_repo: RegistryDBRepository, s3_repo: S3Repository):
        self.db_repo = db_repo
        self.s3_repo = s3_repo

    def create_version(self, model_name: str, user: User, file, source, dataset_reference, metrics_json, params_json):
        model = self.db_repo.get_model_by_name(model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        version_num = self.db_repo.get_last_version_number(model.id) + 1
        s3_key = f"{model_name}/v{version_num}/{file.filename}"
        s3_uri = self.s3_repo.upload_file(file.file, s3_key)

        version_data = {
            "model_id": model.id,
            "version_number": version_num,
            "created_by_id": user.id,
            "source": source,
            "dataset_reference": dataset_reference,
            "s3_artifact_uri": s3_uri
        }

        metrics = json.loads(metrics_json) if metrics_json else {}
        parameters = json.loads(params_json) if params_json else {}

        return self.db_repo.create_version(version_data, metrics, parameters)

    def transition_stage(self, version_id: int, user: User, target_stage: str, reason: str):
        version = self.db_repo.get_version_by_id(version_id)
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")

        if version.current_stage == target_stage:
            raise HTTPException(status_code=400, detail="Already in this stage")

        return self.db_repo.create_transition(version, target_stage.value, user.id, reason)

    def get_download_url(self, version_id: int) -> str:
        version = self.db_repo.get_version_by_id(version_id)
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        return self.s3_repo.generate_presigned_url(version.s3_artifact_uri)