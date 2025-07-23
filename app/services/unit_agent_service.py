from sqlmodel import Session, select
from typing import Sequence
from app.models.unit_agent_link import UnitAgentLink
from app.schemas.unit_agent_link import UnitAgentLinkCreate, UnitAgentLinkRead


def create_unit_agent(session: Session, data: UnitAgentLinkCreate) -> UnitAgentLink:
    from app.models.user import User, Role

    agent = session.get(User, data.agent_id)
    if not agent or agent.role != Role.AGENT:
        raise ValueError("Provided agent_id does not belong to an agent")

    record = UnitAgentLink(**data.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_all_unit_agents(session: Session) -> Sequence[UnitAgentLink]:
    return session.exec(select(UnitAgentLink)).all()


def get_unit_agents_by_unit(session: Session, unit_id: str) -> Sequence[UnitAgentLink]:
    return session.exec(select(UnitAgentLink).where(UnitAgentLink.unit_id == unit_id)).all()


def get_unit_agents_by_agent(session: Session, agent_id: str) -> Sequence[UnitAgentLink]:
    return session.exec(select(UnitAgentLink).where(UnitAgentLink.agent_id == agent_id)).all()