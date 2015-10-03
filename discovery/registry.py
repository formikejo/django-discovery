import os
import socket


class Service(object):
    """
    Models a service.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port


class Registry(object):
    """
    Base class for registries.
    """

    def register(self, service, port, protocol='tcp'):
        raise NotImplementedError()


def get_debug_mode(default):
    debug = os.getenv('DISCOVERY_DEBUG', None)
    if debug is None:
        return default

    return debug.lower() in ["1", "true", "t"]


def get_port_by_name(port):
    try:
        port = socket.getaddrinfo('127.0.0.1', port)[0][-1][-1]
    except socket.gaierror:
        raise ValueError("Could not resolve named port {}".format(port))
    return port


class DockerRegistry(Registry):
    """
    The docker registry uses a docker-client to connect to docker.
    """

    def __init__(self, client, host):
        self.host = host
        self.debug_mode = get_debug_mode(True)
        self.client = client

    def register(self, service, port, protocol='tcp'):
        if isinstance(port, str):
            port = get_port_by_name(port)

        candidates = self.client.containers(filters=dict(
            status='running',
            label='com.docker.compose.service={}'.format(service)
        ))

        if not candidates:
            raise ValueError("No running service found: {}".format(service))

        container = candidates[0]

        service_port = None
        for p in container['Ports']:
            if p['Type'] == protocol and p['PrivatePort'] == port:
                service_port = p['PublicPort']
                break

        if not service_port:
            raise ValueError("Port {} was not defined for container {}".format(port, container['Names'][0]))

        return Service(self.host, service_port)


class DnsRegistry(Registry):
    """
    The DNS registry uses DNS lookups for A and CNAMEs. It uses SRV or environment lookups
    to find port numbers.
    """

    def __init__(self):
        self.debug_mode = get_debug_mode(False)


class EnvironmentRegistry(Registry):

    def __init__(self):
        self.debug_mode = get_debug_mode(False)

    def register(self, service, port, protocol="tcp"):
        if isinstance(port, str):
            port = get_port_by_name(port)

        service_key = "{}_PORT_{}_{}_ADDR".format(service.upper(), port, protocol.upper())
        port_key = "{}_PORT_{}_{}_PORT".format(service.upper(), port, protocol.upper())
        env = os.environ

        if service_key not in env:
            raise ValueError("Service {} not found under {}".format(service, service_key))

        if port_key not in env:
            raise ValueError("Port {} not found under {}".format(port, port_key))

        return Service(env[service_key], int(env[port_key]))
