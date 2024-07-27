#!/usr/bin/env sh

docker run -p 127.0.0.1:5000:5000 --rm -it "$(docker build -q .)"