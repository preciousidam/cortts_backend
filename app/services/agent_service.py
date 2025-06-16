from sqlmodel import Session, select
from app.models.agent import Agent


def create_agent(session: Session, data):
    agent = Agent(**data.model_dump())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def get_all_agents(session: Session):
    return session.exec(select(Agent).where(Agent.deleted == False)).all()


def get_agent_by_id(session: Session, agent_id: str):
    return session.get(Agent, agent_id)


def update_agent(session: Session, agent_id: str, data):
    agent = session.get(Agent, agent_id)
    if not agent or agent.deleted:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def soft_delete_agent(session: Session, agent_id: str, reason: str):
    agent = session.get(Agent, agent_id)
    if agent:
        agent.deleted = True
        agent.reason_for_delete = reason
        session.add(agent)
        session.commit()
    return agent