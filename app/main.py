import shutil
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .auth import verify_api_key
from .downloader import download_video, get_formats

app = FastAPI(
    title="yt-dlp API",
    description=(
        "Download YouTube (and other) videos via a simple HTTP API. "
        "Designed for use with iPhone Shortcuts."
    ),
    version="1.0.0",
)


class DownloadRequest(BaseModel):
    url: str = Field(..., description="Video URL to download")
    quality: Optional[int] = Field(
        None,
        description="Video height cap in pixels: 1080, 720, 480, or 0 for best. "
        "Omit to use the server default (DEFAULT_QUALITY in .env).",
    )
    format_id: Optional[str] = Field(
        None,
        description="Raw yt-dlp format ID, e.g. '137+140'. Overrides quality when set.",
    )


@app.get("/health", tags=["System"], summary="Health check")
def health():
    """Returns 200 OK when the service is running."""
    return {"status": "ok"}


@app.post(
    "/download",
    tags=["Video"],
    summary="Download a video",
    response_description="MP4 video file streamed directly to the client",
    dependencies=[Depends(verify_api_key)],
)
def download(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Download a video from the given URL and stream it as an MP4 file.

    The temporary file is deleted automatically after the response has been sent.
    Authenticate with the `X-Api-Key` header.
    """
    try:
        file_path, display_name, tmp_dir = download_video(req.url, req.quality, req.format_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Remove the temp directory after the file has been fully sent to the client.
    background_tasks.add_task(shutil.rmtree, tmp_dir, True)

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=display_name,
    )


@app.get(
    "/formats",
    tags=["Video"],
    summary="List available formats",
    dependencies=[Depends(verify_api_key)],
)
def formats(url: str = Query(..., description="Video URL to inspect")):
    """Return all available formats for the given video URL.

    Use the returned `format_id` values in the `/download` endpoint to request a
    specific stream combination.
    """
    try:
        return get_formats(url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
