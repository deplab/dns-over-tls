import os

"""
Environmental variables are in use; all are defined in the Dockerfile
and can be overwritten with `docker -e VAR_NAME="value"
"""

# Get environmental variables and check they exist, otherwise os.getenv fails silently
def get_env_var(env_var):
    var = os.getenv(env_var)
    if not var:
        raise Exception(f"[ERROR] {str(env_var)} environmental variable is not found")
    return var

# Upstream DNS Resolver address
DNS_SERVER = get_env_var("DNS_SERVER")
# CA Certificates path - "/etc/ssl/cert.pem" on alpine:3.19
CA_CERT = get_env_var("CA_CERT")
# Address the DNS Proxy to listen on
HOST_ADDRESS = get_env_var("HOST_ADDRESS")
# Port the DNS Proxy to listen on - must be integer
HOST_PORT = int(get_env_var("HOST_PORT"))