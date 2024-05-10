FROM alpine:3.19

RUN apk add python3

COPY dnsproxy.py /opt/dnsproxy.py

EXPOSE 8053/tcp 8053/udp

ENTRYPOINT ["/usr/bin/python3"]
CMD ["/opt/dnsproxy.py"]