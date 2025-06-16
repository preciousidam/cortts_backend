from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api)

@app.get("/")
def read_root():
    return {"message": "Cortts API is live"}