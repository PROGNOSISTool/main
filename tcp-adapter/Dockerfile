FROM openjdk:13-alpine
RUN apk add --no-cache --update --verbose build-base bash busybox-extras libressl-dev sudo libffi-dev python3-dev py3-pip tcpdump apache-ant iptables curl && \
    rm -rf /var/cache/apk/* /tmp/* /sbin/halt /sbin/poweroff /sbin/reboot && \
    pip3 install --pre "scapy[basic]"
RUN curl -o /usr/bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x /usr/bin/wait-for-it
COPY . /code
WORKDIR /code
RUN ant -f Mapper/build.xml dist
WORKDIR /root
CMD iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP && wait-for-it implementation:44344 -s -- python3 -u /code/Adapter/Adapter.py
