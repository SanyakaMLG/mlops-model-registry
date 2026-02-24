from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, models, versions
from app.init_db import init_admin_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up MLOps Registry API...")
    try:
        init_admin_user()
        print("Database initialization check passed.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        
    yield
    
    print("Shutting down MLOps Registry API...")

app = FastAPI(
    title="MLOps Model Registry API", 
    version="2.0.0",
    description="API for storing and managing machine learning models, their versions, and metadata.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(versions.router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "version": app.version}