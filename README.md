# yt-dlp-online


## Requirements

- [mise](https://mise.jdx.dev/) (Python version management)
- ffmpeg (`sudo apt install ffmpeg`)


## Setup

```bash
# 1. Install Python
mise install

# 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env and set a strong API_KEY
# Set YT_DLP_PATH to the path shown by `command -v yt-dlp` to share the CLI version

# 4. Start the server (for testing)
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```


## Running as a systemd service

Edit `yt-dlp-online.service` and replace `/home/pi/yt-dlp-online` with the actual path to this repository, and `pi` with your username.

```bash
sudo cp yt-dlp-online.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now yt-dlp-online
```

Check the status:

```bash
sudo systemctl status yt-dlp-online
```


## API

Interactive documentation is available at `http://<host>:8000/docs` once the server is running.

All endpoints except `/health` require the `X-Api-Key` header.

### Download a video

```
POST /download
X-Api-Key: <your key>
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=...",
  "quality": 1080
}
```

- `quality`: `1080` (default), `720`, `480`, or `0` for best available
- `format_id`: raw yt-dlp format ID (e.g. `"137+140"`), overrides `quality`

Returns the MP4 file as a binary stream.

### List available formats

```
GET /formats?url=https://www.youtube.com/watch?v=...
X-Api-Key: <your key>
```

Returns a JSON array of available format metadata. Use the `format_id` field with `/download`.

### Health check

```
GET /health
```


## iPhone Shortcuts App

1. **Receive Input** — Input: Safari web pages (or share sheet URLs)
2. **Get Contents of URL** — configure as follows:
   - URL: `http://<raspberry-pi-ip>:8000/download`
   - Method: `POST`
   - Headers: add `X-Api-Key` → your API key
   - Request Body: JSON → add key `url`, value: `Shortcut Input` (or the URL variable)
3. **Save to Photo Album** — saves the response to the Photos app

To use from the share sheet in Safari, set the shortcut to accept **Safari web pages** as input and read the page URL at the start.
