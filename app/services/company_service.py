from app.models.company import Company
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.schemas.company import CompanyCreate, CompanyUpdate

def create_company(session: Session, data: CompanyCreate) -> Company:
    '''Create a new company in the database.   
    Args:
        session (Session): SQLAlchemy session.
        data: Data model containing company details.
    Returns:
        Company: The created company object.
    '''
    company = Company(**data.model_dump())
    session.add(company)
    session.commit()
    session.refresh(company)
    return company

def get_all_companies(session: Session) -> list[Company]:
    '''Retrieve all companies that are not deleted.
    Args:
        session (Session): SQLAlchemy session.
    Returns:
        list[Company]: List of all active companies.
    '''
    query = select(Company).where(Company.deleted == False)
    return list(session.exec(query).all())

def get_company_by_id(session: Session, company_id: str) -> Company | None:
    '''Retrieve a company by its ID.
    Args:
        session (Session): SQLAlchemy session.
        company_id (str): The ID of the company to retrieve.
    Returns:
        Company | None: The company object if found, otherwise None.
    '''
    if not company_id:
        return None
    return session.get(Company, company_id)

def update_company(session: Session, company_id: str, data: CompanyUpdate) -> Company | None:
    '''Update an existing company. 
    Args:
        session (Session): SQLAlchemy session.
        company_id (str): The ID of the company to update.
        data: Data model containing updated company details.
    Returns:
        Company | None: The updated company object if successful, otherwise None.
    '''
    company = session.get(Company, company_id)
    if not company or company.deleted:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    company.updated_at = datetime.now(timezone.utc)
    session.add(company)
    session.commit()
    session.refresh(company)
    return company

def soft_delete_company(session: Session, company_id: str, reason: str) -> Company | None:
    '''Soft delete a company by marking it as deleted.
    Args:
        session (Session): SQLAlchemy session.
        company_id (str): The ID of the company to delete.
        reason (str): Reason for deletion.
    Returns:
        Company: The soft-deleted company object.
    '''
    if not company_id:
        return None
    company = session.get(Company, company_id)
    if company:
        company.deleted = True
        company.reason_for_delete = reason
        session.add(company)
        session.commit()
    return company