from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.services.agent_service import (
    create_agent, get_all_agents, get_agent_by_id,
    update_agent, soft_delete_agent
)

router = APIRouter()


@router.post("/", response_model=AgentRead)
def create(data: AgentCreate, session: Session = Depends(get_session)):
    return create_agent(session, data)


@router.get("/", response_model=list[AgentRead])
def all(session: Session = Depends(get_session)):
    return get_all_agents(session)


@router.get("/{agent_id}", response_model=AgentRead)
def get(agent_id: str, session: Session = Depends(get_session)):
    agent = get_agent_by_id(session, agent_id)
    if not agent or agent.deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=AgentRead)
def update(agent_id: str, data: AgentUpdate, session: Session = Depends(get_session)):
    agent = update_agent(session, agent_id, data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/{agent_id}", response_model=AgentRead)
def soft_delete(agent_id: str, reason: str, session: Session = Depends(get_session)):
    agent = soft_delete_agent(session, agent_id, reason)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent