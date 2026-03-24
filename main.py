from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from functions.downlaod_api import download_audio_api, download_video_api

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

@app.get("/download-video")
def download_video(link: str = Query(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    return download_video_api(link, background_tasks)


    # run cmd  ------------>  uvicorn main:app --reload --port 8080
