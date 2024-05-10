import ssl
import socket
import socketserver
import threading
import time
import sys

# Cloudflare DNS Resolver address
DNS_SERVER = "1.1.1.1"
# CA Certificates available on alpine:3.19
CA_CERT = "/etc/ssl/cert.pem"

def request_handler(protocol, request, dns_server=DNS_SERVER, ca_cert=CA_CERT):
    try:
        # Destination dns resolver listens on port 853 and supports TLS 1.2 and 1.3
        # Docs for Cloudflare DoT - https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-tls
        server = (dns_server, 853)
        # Handle TLS and use TLS version v1.2
        tls_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        tls_context.verify_mode = ssl.CERT_REQUIRED
        tls_context.check_hostname = True
        tls_context.load_verify_locations(ca_cert)

        # Create a TCP/UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(60)

            # Wrap the TCP/UDP socket into the TLS context
            with tls_context.wrap_socket(sock, server_hostname=dns_server) as secure_sock:
                secure_sock.connect(server)

                # Query upstream dns server over a TLS wrapped TCP/UDP socket
                if protocol == 'tcp': # handle TCP requests
                    secure_sock.sendall(request)
                    return secure_sock.recv(1024)
                elif protocol == 'udp': # Handle UDP requests
                    message = "\x00".encode() + chr(len(request)).encode() + request
                    secure_sock.send(message)
                    return secure_sock.recv(1024)[2:]
    except Exception as e:
        # Raise an exception if any error occurs
        raise Exception(f"[ERROR] Got the following error while handling the request with the request_handler function: {str(e)}")
    finally:
        # Close the socket after completion or on error
        secure_sock.close()


# Create threaded TCP and UDP servers
class tcp_server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
class udp_server(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

# Create TCP and UDP requesters
class tcp_requester(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.request.sendall(request_handler("tcp", self.request.recv(1024)))
        except Exception as e:
            raise Exception(f"[ERROR] Got the following error while handling the request with the tcp_requester: {str(e)}")
class udp_requester(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            # 
            request, socket = self.request
            socket.sendto(request_handler("udp", request), self.client_address)
        except Exception as e:
            raise Exception(f"[ERROR] Got the following error while handling the request with the udp_requester: {str(e)}")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 53

    servers = [
        tcp_server((HOST, PORT), tcp_requester),
        udp_server((HOST, PORT), udp_requester)
    ]
    # Run the TCP and UDP servers set above in a threaded fashion
    for server in servers:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
    
    # Keep waiting
    try:
        while True:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    # Shut down TCP and UDP servers
    finally:
        for server in servers:
            server.shutdown()