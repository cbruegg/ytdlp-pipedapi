#!/usr/bin/env sh

docker run -p 5000:5000 --rm -it "$(docker build -q .)"