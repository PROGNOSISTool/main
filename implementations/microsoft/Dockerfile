FROM ubuntu as build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential ca-certificates cmake wget git
RUN git clone --recursive --depth=1 https://github.com/microsoft/msquic.git /src
WORKDIR /src/Debug
RUN chmod +x /src/scripts/install-powershell-docker.sh && /src/scripts/install-powershell-docker.sh
ENV     PATH="/root/.dotnet/tools:${PATH}"
RUN     cmake -DQUIC_ENABLE_LOGGING=OFF -DQUIC_BUILD_TEST=OFF ..
RUN     cmake --build .

FROM debian as runtime
RUN apt-get update && apt-get install -y ca-certificates libatomic1 && rm -rf /var/lib/apt/lists/*
COPY --from=build /src/Debug/bin/Release/quicinteropserver /usr/local/bin/quicinteropserver
RUN chmod +x /usr/local/bin/quicinteropserver
COPY --from=build /src/Debug/bin/Release/*.so /usr/local/lib/
RUN chmod a+rwx,g-w,o-w /usr/local/lib/libmsquic.so
RUN ldconfig
COPY ./crypto/ /crypto/
RUN cp /crypto/rootCA.crt /usr/local/share/ca-certificates/ && update-ca-certificates
RUN mkdir /web && echo "Hello World!" >> /web/index.html
ENTRYPOINT ["/usr/local/bin/quicinteropserver"]
CMD ["-listen:0.0.0.0", "-root:/web", "-file:/crypto/cert.crt", "-key:/crypto/cert.key", "-retry:1", "-port:4433"]
