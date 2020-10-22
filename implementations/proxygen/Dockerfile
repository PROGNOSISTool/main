FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install sudo tzdata git curl wget
RUN git clone https://github.com/facebook/proxygen /build
RUN cd /build/proxygen && ./build.sh --with-quic && ./install.sh
ENTRYPOINT ["/build/proxygen/_build/bin/hq"]
CMD ["--mode=server", "--port=4433", "--host=0.0.0.0"]
