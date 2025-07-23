from sqlmodel import Session, select
from app.models.project import Project
from datetime import datetime, timezone
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectList, ProjectRead, ProjectReplace
from app.schemas.paging import Paging
from app.utility.paging import paginate

def create_project(session: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

def get_all_projects(session: Session, paging: Paging) -> dict[str, list[Project] | int]:
    query = select(Project).where(Project.deleted == False)
    projects, total = paginate(session, query, paging)
    
    return {"data": projects, "total": total}

def get_project_by_id(session: Session, project_id: str) -> Project | None:
    return session.get(Project, project_id)

def soft_delete_project(session: Session, project_id: str, reason: str) -> Project | None:
    project = session.get(Project, project_id)
    if project:
        project.deleted = True
        project.reason_for_delete = reason
        project.updated_at = datetime.now(timezone.utc)
        session.add(project)
        session.commit()
    return project

def update_project(session: Session, project_id: str, data: ProjectUpdate) -> Project | None:
    project = session.get(Project, project_id)
    if not project or project.deleted:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    project.updated_at = datetime.now(timezone.utc)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

def replace_project(session: Session, project_id: str, data: ProjectReplace) -> Project | None:
    project = session.get(Project, project_id)
    if not project or project.deleted:
        return None
    for field, value in data.model_dump().items():
        setattr(project, field, value)
    project.updated_at = datetime.now(timezone.utc)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project