import os
import re
from discovery.registry import DockerRegistry, DnsRegistry


services = None


def initialize():
    """
    Initialize the discovery service. This is done automatically when discovery is imported, but it can be used
    to reinitialize the service.
    """
    global services

    docker_host = os.getenv('DOCKER_HOST')

    if docker_host:
        from docker.client import Client
        from docker.utils import kwargs_from_env

        ip = re.match(r'.*?://(.*?):\d+', docker_host).group(1)

        kwargs = kwargs_from_env(assert_hostname=False)
        client = Client(**kwargs)

        services = DockerRegistry(client, ip)
    else:
        services = DnsRegistry()
