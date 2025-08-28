from fastapi import APIRouter
from app.api.routes import project, upload, unit, payment, document, unit_agent_link, user, notification, push_token, company, auth, dashboard
api = APIRouter(prefix='/api/v1')

api.include_router(auth.router, prefix="/auth", tags=["Auth"])
api.include_router(project.router, prefix="/project", tags=["Project"])
api.include_router(payment.router, prefix="/payment", tags=["Payment"])
api.include_router(unit.router, prefix="/unit", tags=["Unit"])
api.include_router(user.router, prefix="/users", tags=["Users"])
api.include_router(document.router, prefix="/document", tags=["Document"])
api.include_router(unit_agent_link.router, prefix="/unit_agents", tags=["Agent", "Unit"])
api.include_router(upload.router, prefix="/upload", tags=["Upload"])
api.include_router(notification.router, prefix="/notification", tags=["Notification"])
api.include_router(push_token.router, prefix="/push-token", tags=["Push Token"])
api.include_router(company.router, prefix="/company", tags=["Company"])
api.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])