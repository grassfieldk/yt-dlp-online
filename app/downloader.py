import os
import shutil
import tempfile
from typing import Optional

import yt_dlp

from .config import settings

# Maps quality preset (video height in pixels) to a yt-dlp format selection string.
# Each entry falls back through progressively looser constraints so a result is
# always produced even when the requested height is unavailable.
#
# Priority: H.264 (avc1) video + AAC (mp4a) audio — required for iOS Photos compatibility.
# VP9 / AV1 streams are intentionally excluded from the first-choice selectors.
_QUALITY_FORMAT: dict[int, str] = {
    1080: (
        "bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]"
        "/bestvideo[height<=1080][vcodec^=avc1]+bestaudio"
        "/bestvideo[height<=1080]+bestaudio[acodec^=mp4a]"
        "/bestvideo[height<=1080]+bestaudio"
        "/best[height<=1080]/best"
    ),
    720: (
        "bestvideo[height<=720][vcodec^=avc1]+bestaudio[acodec^=mp4a]"
        "/bestvideo[height<=720][vcodec^=avc1]+bestaudio"
        "/bestvideo[height<=720]+bestaudio[acodec^=mp4a]"
        "/bestvideo[height<=720]+bestaudio"
        "/best[height<=720]/best"
    ),
    480: (
        "bestvideo[height<=480][vcodec^=avc1]+bestaudio[acodec^=mp4a]"
        "/bestvideo[height<=480][vcodec^=avc1]+bestaudio"
        "/bestvideo[height<=480]+bestaudio[acodec^=mp4a]"
        "/bestvideo[height<=480]+bestaudio"
        "/best[height<=480]/best"
    ),
    # 0 = uncapped, pick the best available quality
    0: (
        "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]"
        "/bestvideo[vcodec^=avc1]+bestaudio"
        "/bestvideo+bestaudio/best"
    ),
}


def _resolve_format(quality: Optional[int], format_id: Optional[str]) -> str:
    """Return the yt-dlp format string to use for a download request."""
    if format_id:
        return format_id
    q = quality if quality is not None else settings.default_quality
    return _QUALITY_FORMAT.get(q, _QUALITY_FORMAT[1080])


def download_video(
    url: str,
    quality: Optional[int] = None,
    format_id: Optional[str] = None,
) -> tuple[str, str, str]:
    """Download a video and return (file_path, display_filename, tmp_dir).

    The caller is responsible for removing tmp_dir when the file is no longer needed.
    On failure, tmp_dir is removed automatically before re-raising the exception.
    """
    fmt = _resolve_format(quality, format_id)
    tmp_dir = tempfile.mkdtemp(dir=settings.temp_dir)

    ydl_opts = {
        "format": fmt,
        # Use the video ID as the filename to avoid filesystem-unsafe characters.
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        mp4_files = [f for f in os.listdir(tmp_dir) if f.endswith(".mp4")]
        if not mp4_files:
            raise RuntimeError("Download completed but no mp4 file was produced")

        file_path = os.path.join(tmp_dir, mp4_files[0])

        # Build a safe display filename from the video title for Content-Disposition.
        title = info.get("title", "video")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()
        display_name = f"{safe_title or 'video'}.mp4"

    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return file_path, display_name, tmp_dir


def get_formats(url: str) -> list[dict]:
    """Return available format metadata for the given URL without downloading."""
    ydl_opts = {"quiet": True, "no_warnings": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return [
        {
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution") or f"{f.get('width', '?')}x{f.get('height', '?')}",
            "fps": f.get("fps"),
            "vcodec": f.get("vcodec"),
            "acodec": f.get("acodec"),
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "format_note": f.get("format_note"),
        }
        for f in info.get("formats", [])
    ]
