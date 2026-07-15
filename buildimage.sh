docker build \
  --build-arg http_proxy=$http_proxy \
  --build-arg https_proxy=$https_proxy \
  --build-arg all_proxy=$all_proxy \
  --build-arg HTTP_PROXY=$HTTP_PROXY \
  --build-arg HTTPS_PROXY=$HTTPS_PROXY \
  --build-arg ALL_PROXY=$ALL_PROXY \
 -f docker/Dockerfile.pawbench-qwenpaw -t pawbench-openclaw:4.14 .
