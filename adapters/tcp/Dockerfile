FROM python:3.11-alpine
RUN apk add --no-cache --update sudo openjdk13 apache-ant build-base bash busybox-extras libffi-dev tcpdump libpcap-dev iptables curl libpq-dev
RUN pip3 install --pre "scapy[basic]" pcapy-ng impacket sqlalchemy psycopg2 jsons
RUN curl -o /usr/bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x /usr/bin/wait-for-it
COPY . /code
WORKDIR /code
RUN ant -f Mapper/build.xml dist
WORKDIR /root
CMD iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP && wait-for-it implementation:44344 -s -- python3 -u /code/Adapter/Adapter.py
