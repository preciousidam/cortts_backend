from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.unit_agent_link import UnitAgentLinkCreate, UnitAgentLinkRead
from app.services.unit_agent_service import (
    create_unit_agent, get_all_unit_agents,
    get_unit_agents_by_unit, get_unit_agents_by_agent
)
from app.auth.dependencies import get_current_user
from app.models.user import Role

router = APIRouter()


@router.post("/", response_model=UnitAgentLinkRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT]))])
def create(data: UnitAgentLinkCreate, session: Session = Depends(get_session)):
    return create_unit_agent(session, data)


@router.get("/", response_model=list[UnitAgentLinkRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT]))])
def all(session: Session = Depends(get_session)):
    return get_all_unit_agents(session)


@router.get("/unit/{unit_id}", response_model=list[UnitAgentLinkRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT]))])
def by_unit(unit_id: str, session: Session = Depends(get_session)):
    return get_unit_agents_by_unit(session, unit_id)


@router.get("/agent/{agent_id}", response_model=list[UnitAgentLinkRead], dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT]))])
def by_agent(agent_id: str, session: Session = Depends(get_session)):
    return get_unit_agents_by_agent(session, agent_id)