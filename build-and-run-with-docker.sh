#!/usr/bin/env sh

docker run --rm -it "$(docker build -q .)"