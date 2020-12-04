FROM ubuntu:18.04 as build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential git curl wget lsb-release sudo python tzdata
WORKDIR /root
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
ENV PATH="$PATH:/root/depot_tools"
RUN mkdir /root/chromium
WORKDIR /root/chromium
RUN fetch --nohooks --no-history chromium
WORKDIR /root/chromium/src
RUN ./build/install-build-deps.sh --no-prompt
RUN gclient runhooks
RUN gn gen out/Default
ENV symbol_level=0
ENV blink_symbol_level=0
RUN autoninja -C out/Default quic_server

FROM ubuntu:18.04 as runtime
RUN apt-get update && apt-get install -y libglib2.0-0 libnss3 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=build /root/chromium/src/out/Default/*.so /usr/lib/
RUN ldconfig
COPY --from=build /root/chromium/src/out/Default/quic_server /usr/bin/
COPY ./crypto/ /crypto/
RUN cp /crypto/rootCA.crt /usr/local/share/ca-certificates/ && update-ca-certificates
COPY ./quic.tiferrei.com/ /quic.tiferei.com/
ENTRYPOINT ["/usr/bin/quic_server"]
CMD ["--certificate_file=/crypto/cert.crt", "--key_file=/crypto/key.pkcs8", "--port=4433", "--v=1", "--quic_ietf_draft", "--quic_response_cache_dir=/quic.tiferrei.com"]
