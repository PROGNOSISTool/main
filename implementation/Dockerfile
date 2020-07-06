FROM rust:1.39 as build

WORKDIR /build

COPY deps/ ./deps/
COPY src/ ./src/
COPY tools/ ./tools/
COPY Cargo.toml .

RUN apt-get update && apt-get install -y cmake golang-go && \
    rm -rf /var/lib/apt/lists/*

RUN cargo build --manifest-path tools/apps/Cargo.toml

##
## quiche-base: quiche image for apps
##
FROM debian:latest as quiche-base

RUN apt-get update && apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build \
     /build/tools/apps/target/debug/quiche-client \
     /build/tools/apps/target/debug/quiche-server \
     /usr/local/bin/
COPY examples/cert.crt examples/cert.key examples/
COPY root root/

ENV PATH="/usr/local/bin/:${PATH}"
ENV RUST_LOG=info
