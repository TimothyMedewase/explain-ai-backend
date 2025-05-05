from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import router
from dotenv import load_dotenv
import os

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI(
    title="Explain AI API",
    description="API for analyzing documents and answering questions about their content",
    version="1.0.0"
)

# Get frontend URL from environment variables or use default values
# Railway will inject your production frontend URL as an env var
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Allow all origins in dev, but you can restrict this in production
production_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
allowed_origins = production_origins if production_origins else [frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Explain AI API. Use /process endpoint to analyze documents."}

app.include_router(router)