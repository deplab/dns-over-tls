FROM alpine:3.19

    # Upstream DNS Resolver address
ENV DNS_SERVER="1.1.1.1" \
    # CA Certificates path
    CA_CERT="/etc/ssl/cert.pem" \
    # Address the DNS Proxy to listen on
    HOST_ADDRESS="0.0.0.0" \
    # Port the DNS Proxy to listen on
    HOST_PORT=53

RUN apk add --no-cache python3

COPY src/* /opt/

EXPOSE 8153/tcp 8153/udp

ENTRYPOINT ["/usr/bin/python3"]
CMD ["/opt/__main__.py"]