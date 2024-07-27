import os
import subprocess
import sys

from yt_dlp import YoutubeDL
from flask import Flask, request, jsonify, Response, stream_with_context

app = Flask(__name__)


@app.route('/streams/<id>')
def get_streams(id: str):
    info = get_video_info(id)

    jpg_thumbnails = [x for x in info["thumbnails"] if x["url"].endswith(".jpg")]
    thumbnail = max(jpg_thumbnails, key=lambda x: x.get("preference", -1000))

    return {
        "title": info["title"],
        "thumbnailUrl": thumbnail["url"],
        "audioStreams": to_piped_audio_streams(info["formats"], id),
        "videoStreams": to_piped_video_streams(info["formats"], id)
    }


@app.route('/audio/<id>/<format_id>')
def get_audio(id: str, format_id: str):
    return get_media(id, format_id, "audio")


@app.route('/video/<id>/<format_id>')
def get_video(id: str, format_id: str):
    return get_media(id, format_id, "video")


def get_media(id: str, format_id: str, media_type: str):
    outfile_name = f'{id}-{media_type}.dat'

    env = {}
    env.update(os.environ)
    p = subprocess.Popen(
        ["python3", "-m", "yt_dlp", f"https://www.youtube.com/watch?v={id}", "-f", format_id, "-o", "-"],
        env=env,
        stdout=subprocess.PIPE)

    return Response(
        stream_with_context(read_from_subprocess(p)),
        headers={
            'Content-Disposition': f'attachment; filename={outfile_name}'
        }
    )


def to_piped_audio_streams(streams, video_id: str):
    host_url = get_host_url()
    filtered_streams = [x for x in streams if "quality" in x and x["ext"] != "html"]
    sorted_streams = sorted(filtered_streams, key=lambda x: x["quality"], reverse=True)
    return [{
        "url": f"{host_url}audio/{video_id}/{x['format_id']}",
        "format": x["audio_ext"].upper(),
        "quality": str(x["abr"]) + "kbps",
        "mimeType": "audio/" + x["audio_ext"].replace("m4a", "mp4"),
        "codec": x["acodec"]
    } for x in sorted_streams if x["ext"] == "m4a" and not x["format_id"].endswith("drc")]


def to_piped_video_streams(streams, video_id: str):
    host_url = get_host_url()
    filtered_streams = [x for x in streams if "quality" in x and x["ext"] != "html"]
    sorted_streams = sorted(filtered_streams, key=lambda x: x["quality"], reverse=True)
    return [{
        "url": f"{host_url}video/{video_id}/{x['format_id']}",
        "format": x["video_ext"].upper().replace("MP4", "MPEG_4"),
        "quality": x["format_note"],
        "mimeType": "video/" + x["video_ext"],
        "codec": x["vcodec"],
        "videoOnly": x["acodec"] == "none"
    } for x in sorted_streams if "format_note" in x and x["ext"] == "mp4" and x["vcodec"] != "none"]


def get_video_info(id: str):
    url = f"https://www.youtube.com/watch?v={id}"
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


def get_host_url() -> str:
    forwarded = request.headers.get("X-Forwarded-Host", "")
    if forwarded != "":
        return "https://" + forwarded + "/"
    else:
        return request.host_url


def read_from_subprocess(p):
    while True:
        buf = p.stdout.read(8192)
        if buf:
            yield buf
        else:
            break


if __name__ == '__main__':
    args = sys.argv[1:]
    port = 5000 if len(args) == 0 else int(args[0])
    debug = False if len(args) <= 1 else args[1] == "debug"
    app.run(port=port, debug=debug)

# TODO Next steps:
#   3. Deploy to Oracle server
