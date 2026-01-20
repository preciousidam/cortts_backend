from typing import Any, List, Tuple
from sqlmodel import Session, select, func
from app.schemas.paging import Paging

def paginate(
    session: Session,
    query: Any,
    paging: Paging
) -> Tuple[List[Any], int]:
    """
    Paginate a SQLModel query.

    Returns: (items, total)
    - items: List of results on the requested page
    - total: Total count for the query
    """

    items = session.exec(query.limit(paging.limit).offset(paging.skip)).all()
    total = session.exec(select(func.count()).select_from(query.subquery())).one() or 0
    return items, total