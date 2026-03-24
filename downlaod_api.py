from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse 
import yt_dlp
import tempfile
import os
import urllib.parse

TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


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
    

def iterfile_and_delete(file_path):
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                yield chunk
    finally:
        # 🔥 delete after streaming completes
        try:
            os.remove(file_path)
        except:
            pass


def download_video_api(link: str):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'restrictfilenames': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)

        # Fix merged filename
        base, _ = os.path.splitext(file_path)
        final_file = base + ".mp4"

        filename = os.path.basename(final_file)
        encoded_filename = urllib.parse.quote(filename)

        return StreamingResponse(
            iterfile_and_delete(final_file),  # 🔥 auto delete here
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading {link}:) {e}") 
