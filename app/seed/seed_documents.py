from sqlmodel import Session, select
from app.db.session import engine
from app.models.document import DocumentTemplate, SignedDocument, MediaFile
from app.models.unit import Unit
from app.models.user import User, Role
from datetime import datetime, timezone


def seed_documents():
    with Session(engine) as session:
        unit = session.exec(select(Unit)).first()
        client = session.exec(select(User).where(User.role == Role.CLIENT)).first()
        agent = session.exec(select(User).where(User.role == Role.AGENT)).first()

        media_file = MediaFile(
            file_name="Sale Agreement - Sample.pdf",
            file_type="application/pdf",
            file_path="/media/sale_agreement_sample.pdf",
            file_size=204800,  # 200 KB
            uploaded_by=agent.id if agent else client.id if client else None,
        )
        session.add(media_file)
        session.commit()
        session.refresh(media_file)
        
        media_file2 = MediaFile(
            file_name="Sale Agreement - Sample.pdf",
            file_type="application/pdf",
            file_path="/media/sale_agreement_sample.pdf",
            file_size=204800,  # 200 KB
            uploaded_by=agent.id if agent else  None,
        )
        session.add(media_file2)
        session.commit()
        session.refresh(media_file2)

        media_file3 = MediaFile(
            file_name="Sale Agreement - Sample.pdf",
            file_type="application/pdf",
            file_path="/media/sale_agreement_sample.pdf",
            file_size=204800,  # 200 KB
            uploaded_by=client.id if client else None,
        )
        session.add(media_file3)
        session.commit()
        session.refresh(media_file3)

        if unit:
            template = DocumentTemplate(
                name="Sale Agreement Template",
                media_file_id=media_file.id ,
                unit_id=unit.id
            )
            session.add(template)

            signed_by_client = SignedDocument(
                name="Signed Sale Agreement - Client",
                media_file_id=media_file3.id,
                unit_id=unit.id,
                client_id=client.id if client else None
            )
            signed_by_agent = SignedDocument(
                name="Signed Sale Agreement - Agent",
                media_file_id=media_file2.id,
                unit_id=unit.id,
                agent_id=agent.id if agent else None
            )
            session.add_all([signed_by_client, signed_by_agent])
            session.commit()


if __name__ == "__main__":
    seed_documents()