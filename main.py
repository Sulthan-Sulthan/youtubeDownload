from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from downlaod_api import download_audio_api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"] 
)

@app.get("/download")
def download_audio(link: str = Query(...)):
    return download_audio_api(link)
