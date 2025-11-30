from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PolicyPARAKH API",
    description="Backend API for PolicyPARAKH - The AI Consumer Guardian",
    version="2.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:8000",
]

from .routers import audit, chat, medical, courtroom, admin

# ... (previous code)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(audit.router)
app.include_router(chat.router)
app.include_router(medical.router)
app.include_router(courtroom.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "PolicyPARAKH API is running 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
