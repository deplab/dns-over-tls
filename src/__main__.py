import dnsproxy
import config
import threading
import time
import sys

if __name__ == "__main__":
    host, port = config.HOST_ADDRESS, config.HOST_PORT

    servers = [
        dnsproxy.tcp_server((host, port), dnsproxy.tcp_requester),
        dnsproxy.udp_server((host, port), dnsproxy.udp_requester)
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