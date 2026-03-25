from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .api import auth, stations, patrol, alarms, devices

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(patrol.router, prefix="/api")
app.include_router(alarms.router, prefix="/api")
app.include_router(devices.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.VERSION}
