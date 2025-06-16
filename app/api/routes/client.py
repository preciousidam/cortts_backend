from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.services.client_service import (
    create_client, get_all_clients, get_client_by_id,
    update_client, soft_delete_client
)

router = APIRouter()


@router.post("/", response_model=ClientRead)
def create(data: ClientCreate, session: Session = Depends(get_session)):
    return create_client(session, data)


@router.get("/", response_model=list[ClientRead])
def all(session: Session = Depends(get_session)):
    return get_all_clients(session)


@router.get("/{client_id}", response_model=ClientRead)
def get(client_id: str, session: Session = Depends(get_session)):
    client = get_client_by_id(session, client_id)
    if not client or client.deleted:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientRead)
def update(client_id: str, data: ClientUpdate, session: Session = Depends(get_session)):
    client = update_client(session, client_id, data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/{client_id}", response_model=ClientRead)
def soft_delete(client_id: str, reason: str, session: Session = Depends(get_session)):
    client = soft_delete_client(session, client_id, reason)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client