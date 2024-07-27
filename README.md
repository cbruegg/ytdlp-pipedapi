# ytdlp-pipedapi

I've developed the [EmptyPipe app](https://github.com/cbruegg/EmptyPipe) for iOS
that lets users download videos from [Piped instances](https://github.com/TeamPiped/Piped).

Unfortunately, Piped instances are often slow or unreliable, so I've developed a small Docker container
that behaves roughly like the API of a Piped instance, but uses yt-dlp to download videos.

## Usage

1. Install Docker
2. Clone this repository
3. `cd ytdlp-pipedapi`
4. Run `docker-compose up -d`

ytdlp-pipedapi is now listening on `localhost:5000`. To change the port (e.g. to 1234), just edit the `compose.yaml` to say `1234:5000`.

To expose the API to the internet, you can use a reverse proxy like Caddy or Nginx. Here's an example Nginx config:

```
server {
	server_name ytdlppiped.yourdomain.com;

	listen 80;
	listen [::]:80;
	location / {
		proxy_set_header X-Forwarded-Host $http_host;
		proxy_pass http://127.0.0.1:5000;
		gzip off;
	}

}
```

To set up HTTPS, you can use [Certbot](https://certbot.eff.org/).