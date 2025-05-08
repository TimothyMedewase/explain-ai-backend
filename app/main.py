from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import router
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI(
    title="Explain AI API",
    description="API for analyzing documents and answering questions about their content",
    version="1.0.0"
)

# Get frontend URL from environment variables or use default values
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")

# Process the allowed origins
production_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
allowed_origins = production_origins if production_origins else [frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"]

# Log the CORS configuration for debugging
logger.info(f"Frontend URL: {frontend_url}")
logger.info(f"ALLOWED_ORIGINS environment variable: {allowed_origins_str}")
logger.info(f"Configured CORS allowed origins: {allowed_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Allow access to custom headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to Explain AI API. Use /process endpoint to analyze documents."}

# Add a debug endpoint to check CORS config
@app.get("/debug/cors")
async def debug_cors():
    """Endpoint to check CORS configuration for debugging"""
    return {
        "frontend_url": frontend_url,
        "allowed_origins": allowed_origins,
        "allowed_origins_env": os.getenv("ALLOWED_ORIGINS", "Not set")
    }

app.include_router(router)