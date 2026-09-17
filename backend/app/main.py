from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_error_handlers
from app.routers import campaigns, companies, discovery, emails, events, leads, replies, tracking

app = FastAPI(title="ThinkDataX Lead Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(companies.router)
app.include_router(campaigns.router)
app.include_router(discovery.router)
app.include_router(leads.router)
app.include_router(events.router)
app.include_router(replies.router)
app.include_router(emails.router)
app.include_router(tracking.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}