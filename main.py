import os
import subprocess
import sys

from yt_dlp import YoutubeDL
from flask import Flask, request, jsonify, Response, stream_with_context

app = Flask(__name__)

DEMO_ID = "big_buck_bunny"


@app.route('/streams/<id>')
def get_streams(id: str):
    if id == DEMO_ID:
        return {
            "title": "Big Buck Bunny",
            "thumbnailUrl": f"{get_host_url()}demodata/thumbnail.jpg",
            "audioStreams": [
                {
                    "url": f"{get_host_url()}demodata/audio-140-demo.dat",
                    "format": "M4A",
                    "quality": "128kbps",
                    "mimeType": "audio/mp4",
                    "codec": "mp4a.40.5"
                }
            ],
            "videoStreams": [
                {
                    "url": f"{get_host_url()}demodata/video-136-demo.dat",
                    "format": "MPEG_4",
                    "quality": "1080p",
                    "mimeType": "video/mp4",
                    "codec": "avc1.640028",
                    "videoOnly": True
                }
            ]
        }

    info = get_video_info(id)

    jpg_thumbnails = [x for x in info["thumbnails"] if x["url"].endswith(".jpg")]
    thumbnail = max(jpg_thumbnails, key=lambda x: x.get("preference", -1000))

    return {
        "title": info["title"],
        "thumbnailUrl": thumbnail["url"],
        "audioStreams": to_piped_audio_streams(info["formats"], id),
        "videoStreams": to_piped_video_streams(info["formats"], id)
    }


@app.route('/demodata/<filename>')
def get_demodata(filename):
    return app.send_static_file(f'demodata/{filename}')


@app.route('/audio/<id>/<format_id>')
def get_audio(id: str, format_id: str):
    return get_media(id, format_id, "audio")


@app.route('/video/<id>/<format_id>')
def get_video(id: str, format_id: str):
    return get_media(id, format_id, "video")


def get_media(id: str, format_id: str, media_type: str):
    outfile_name = f'{id}-{media_type}.dat'

    video_info = get_video_info(id)
    selected_format = [x for x in video_info["formats"] if x["format_id"] == format_id][0]
    if "filesize" in selected_format:
        filesize = selected_format["filesize"]
    else:
        filesize = None

    env = {}
    env.update(os.environ)
    p = subprocess.Popen(
        ["python3", "-m", "yt_dlp", f"https://www.youtube.com/watch?v={id}", "-f", format_id, "-o", "-"],
        env=env,
        stdout=subprocess.PIPE)

    headers = {
        'Content-Disposition': f'attachment; filename={outfile_name}'
    }
    if filesize is not None:
        headers["Content-Length"] = str(filesize)
    return Response(
        stream_with_context(read_from_subprocess(p)),
        headers=headers
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


# second parameter is an optional format id
def get_video_info(id: str, format_id: str or None = None):
    url = f"https://www.youtube.com/watch?v={id}"
    ydl_opts = {}
    if format_id is not None:
        ydl_opts["format"] = format_id
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
