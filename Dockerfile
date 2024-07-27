# syntax=docker/dockerfile:1
FROM python:3.12-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers ffmpeg
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["./run-self-updating.sh"]