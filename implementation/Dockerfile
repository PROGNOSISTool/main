# Adapted from https://github.com/cloudflare/quiche/blob/master/Dockerfile
FROM rust:1.44.1 as build

WORKDIR /build

COPY src/ ./src/
COPY Cargo.toml Cargo.lock ./

RUN apt-get update && apt-get install -y cmake golang-go && \
    rm -rf /var/lib/apt/lists/*

RUN cargo build

##
## quiche-base: quiche image for apps
##
FROM debian:latest as quiche-base

RUN apt-get update && apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build \
     /build/target/debug/quiche-client \
     /build/target/debug/quiche-server \
     /usr/local/bin/

COPY --from=build \
     /build/src/bin/cert.crt \
     /build/src/bin/cert.key \
     ./crypto/

ENV PATH="/usr/local/bin/:${PATH}"
ENV RUST_LOG=info

RUN mkdir web && echo "Hello World!" > web/index.html

ENTRYPOINT ["quiche-server"]
CMD ["--cert", "./crypto/cert.crt", \
    "--key", "./crypto/cert.key", \
    "--listen", "0.0.0.0:4433", \
    "--root", "./web", \
    "--no-grease", \
    "--quick-ack"]
