from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.services.project_service import (
    create_project, get_all_projects, get_project_by_id,
    soft_delete_project, update_project, replace_project
)
from app.schemas.project import (
    ProjectCreate, ProjectRead, ProjectUpdate, ProjectReplace
)
from app.auth.dependencies import get_current_user
from app.models.user import Role

router = APIRouter()

@router.post("/", response_model=ProjectRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create(data: ProjectCreate, session: Session = Depends(get_session)):
    return create_project(session, data)

@router.get("/", response_model=list[ProjectRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def get_all(session: Session = Depends(get_session)):
    return get_all_projects(session)

@router.get("/{project_id}", response_model=ProjectRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def get_by_id(project_id: str, session: Session = Depends(get_session)):
    project = get_project_by_id(session, project_id)
    if not project or project.deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def update(project_id: str, data: ProjectUpdate, session: Session = Depends(get_session)):
    project = update_project(session, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def replace(project_id: str, data: ProjectReplace, session: Session = Depends(get_session)):
    project = replace_project(session, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete(project_id: str, reason: str, session: Session = Depends(get_session)):
    project = soft_delete_project(session, project_id, reason)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}