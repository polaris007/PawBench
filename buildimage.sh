#!/usr/bin/env bash
# Usage: ./buildimage.sh [9.1|8.1|5.28]   (default: 9.1)
# 9.1 builds from the main Dockerfile; 8.1/5.28 use the frozen versioned files.
VER="${1:-9.1}"
case "$VER" in
  9.1) DOCKERFILE="docker/Dockerfile.pawbench-openclaw" ;;
  *)   DOCKERFILE="docker/Dockerfile.pawbench-openclaw-${VER}" ;;
esac

docker build \
  --build-arg http_proxy=$http_proxy \
  --build-arg https_proxy=$https_proxy \
  --build-arg all_proxy=$all_proxy \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg ALL_PROXY=$ALL_PROXY \
 -f "$DOCKERFILE" -t "pawbench-openclaw:${VER}" .
