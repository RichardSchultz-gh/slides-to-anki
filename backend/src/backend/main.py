from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_session

app = FastAPI(title="Anki-KI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Liveness(BaseModel):
    status: Literal["ok"]


class Readiness(BaseModel):
    status: Literal["ok", "unavailable"]
    database: bool


# Liveness ("lebt der Prozess?") hängt bewusst nicht von der DB ab: Ein Neustart der App
# behebt keinen DB-Ausfall und würde nur eine Neustart-Schleife auslösen.
@app.get("/api/health/live")
async def live() -> Liveness:
    return Liveness(status="ok")


# Readiness ("kann die App gerade arbeiten?") für Uptime-Monitore und Load-Balancer, die nur
# den Statuscode auswerten.
@app.get(
    "/api/health/ready",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": Readiness}},
)
async def ready(
    session: Annotated[AsyncSession, Depends(get_session)], response: Response
) -> Readiness:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Readiness(status="unavailable", database=False)
    return Readiness(status="ok", database=True)
