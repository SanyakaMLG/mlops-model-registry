from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.registry import RegisteredModel, ModelVersion, ModelMetric, ModelParameter, StateTransition

class RegistryDBRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_model_by_name(self, name: str) -> Optional[RegisteredModel]:
        return self.db.query(RegisteredModel).filter(RegisteredModel.name == name).first()

    def create_model(self, name: str, description: Optional[str]) -> RegisteredModel:
        model = RegisteredModel(name=name, description=description)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_models(self, limit: int, offset: int) -> List[RegisteredModel]:
        return self.db.query(RegisteredModel).limit(limit).offset(offset).all()

    def get_last_version_number(self, model_id: int) -> int:
        last_version = self.db.query(ModelVersion).filter(ModelVersion.model_id == model_id)\
                              .order_by(ModelVersion.version_number.desc()).first()
        return last_version.version_number if last_version else 0

    def create_version(self, version_data: dict, metrics: dict, parameters: dict) -> ModelVersion:
        version = ModelVersion(**version_data)
        self.db.add(version)
        self.db.flush()

        if metrics:
            for k, v in metrics.items():
                self.db.add(ModelMetric(version_id=version.id, key=str(k), value=float(v)))
        if parameters:
            for k, v in parameters.items():
                self.db.add(ModelParameter(version_id=version.id, key=str(k), value=str(v)))

        self.db.commit()
        self.db.refresh(version)
        return version

    def get_versions(self, model_id: int, stage: Optional[str] = None) -> List[ModelVersion]:
        query = self.db.query(ModelVersion).filter(ModelVersion.model_id == model_id)
        if stage:
            query = query.filter(ModelVersion.current_stage == stage)
        return query.all()

    def get_version_by_id(self, version_id: int) -> Optional[ModelVersion]:
        return self.db.query(ModelVersion).filter(ModelVersion.id == version_id).first()

    def get_transitions(self, version_id: int) -> List[StateTransition]:
        return self.db.query(StateTransition).filter(StateTransition.version_id == version_id).order_by(StateTransition.created_at.desc()).all()

    def create_transition(self, version: ModelVersion, target_stage: str, actor_id: int, reason: Optional[str]) -> StateTransition:
        transition = StateTransition(
            version_id=version.id, from_stage=version.current_stage.value,
            to_stage=target_stage, actor_id=actor_id, reason=reason
        )
        version.current_stage = target_stage
        self.db.add(transition)
        self.db.commit()
        return transition