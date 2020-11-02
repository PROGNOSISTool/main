FROM alpine:latest
RUN apk add --no-cache --update --verbose grep bash nmap-ncat && \
    rm -rf /var/cache/apk/* /tmp/* /sbin/halt /sbin/poweroff /sbin/reboot

ENTRYPOINT ["/usr/bin/ncat"]
CMD ["-l", "-p", "44344", "-k", "-v"]
