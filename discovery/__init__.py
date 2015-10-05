import os
import re
from discovery.registry import DockerRegistry, DnsRegistry, EnvironmentRegistry


services = None


def initialize():
    """
    Initialize the discovery service. This is done automatically when discovery is imported, but it can be used
    to reinitialize the service.
    """
    global services

    discovery_mode = os.getenv('DISCOVERY_MODE')
    docker_host = os.getenv('DOCKER_HOST')

    if not discovery_mode and docker_host:
        discovery_mode = 'docker'

    if not discovery_mode:
        discovery_mode = 'dns'

    if discovery_mode == 'docker':
        if not docker_host:
            raise ValueError("DOCKER_HOST not set")

        from docker.client import Client
        from docker.utils import kwargs_from_env

        ip = re.match(r'.*?://(.*?):\d+', docker_host).group(1)

        kwargs = kwargs_from_env(assert_hostname=False)
        client = Client(**kwargs)

        services = DockerRegistry(client, ip)
    elif discovery_mode == 'env':
        services = EnvironmentRegistry()
    elif discovery_mode == 'dns':
        services = DnsRegistry()
    else:
        raise ValueError("Unknown DISCOVERY_MODE: {}".format(discovery_mode))

initialize()
