from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import router
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI(
    title="Explain AI API",
    description="API for analyzing documents and answering questions about their content",
    version="1.0.0"
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Explain AI API. Use /process endpoint to analyze documents."}

app.include_router(router)