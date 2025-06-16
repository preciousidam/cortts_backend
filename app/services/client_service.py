from sqlmodel import Session, select
from app.models.client import Client

def create_client(session: Session, data):
    client = Client(**data.model_dump())
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

def get_all_clients(session: Session):
    return session.exec(select(Client).where(Client.deleted == False)).all()

def get_client_by_id(session: Session, client_id: str):
    return session.get(Client, client_id)

def update_client(session: Session, client_id: str, data):
    client = session.get(Client, client_id)
    if not client or client.deleted:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

def soft_delete_client(session: Session, client_id: str, reason: str):
    client = session.get(Client, client_id)
    if client:
        client.deleted = True
        client.reason_for_delete = reason
        session.add(client)
        session.commit()
    return client