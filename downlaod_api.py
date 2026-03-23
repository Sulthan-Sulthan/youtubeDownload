from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import tempfile
import os

TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

def download_audio_api(link: str):
    try:
        tmpfile = tempfile.NamedTemporaryFile(dir=TEMP_FOLDER, delete=False)
        tmp_filename = tmpfile.name
        tmpfile.close()

        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'format': 'bestaudio/best',
            'outtmpl': tmp_filename + '.%(ext)s',  # Add extension placeholder
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)

        ext = info.get('ext', 'webm')
        actual_filename = tmp_filename + f".{ext}"

        if not os.path.exists(actual_filename) or os.path.getsize(actual_filename) == 0:
            raise HTTPException(status_code=500, detail="Downloaded file missing or empty")

        def iterfile(file_path):
            with open(file_path, "rb") as f:
                yield from f
            try:
                os.remove(file_path)
            except:
                pass

        return StreamingResponse(
            iterfile(actual_filename),
            media_type=f"audio/{ext}",
            headers={"Content-Disposition": f"attachment; filename=youtube_audio.{ext}"}
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading {link}: {e}")
