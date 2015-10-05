import os
import socket

import dns.resolver


class Service(object):
    """
    Models a service.
    """

    def __init__(self, host, port, secrets):
        self.host = host
        self.port = port
        self.secrets = secrets


class Registry(object):
    """
    Base class for registries.
    """

    def register(self, service, port, protocol='tcp', secrets=None):
        raise NotImplementedError()


def get_debug_mode(default):
    debug = os.getenv('DISCOVERY_DEBUG', None)
    if debug is None:
        return default

    return debug.lower() in ["1", "true", "t"]


def get_port_by_name(port, protocol):
    if isinstance(port, int):
        return port

    try:
        return socket.getservbyname(port, protocol)
    except OSError:
        raise ValueError("Could not resolve named port {}".format(port))


def get_name_by_port(port, protocol):
    if isinstance(port, str):
        return port

    try:
        return socket.getservbyport(port, protocol)
    except OSError:
        raise ValueError("Could not resolve numbered port {}".format(port))


class DockerRegistry(Registry):
    """
    The docker registry uses a docker-client to connect to docker.
    """

    def __init__(self, client, host):
        self.host = host
        self.debug_mode = get_debug_mode(True)
        self.client = client

    def register(self, service, port, protocol='tcp', secrets=None):
        port = get_port_by_name(port, protocol)

        container = self.get_container_for(service)
        service_port = self.get_port_mapping_in(container, port, protocol)

        container_name = container['Names'][0]
        resolved_secrets = self.resolve_secrets_in(container_name, secrets)

        return Service(self.host, service_port, resolved_secrets)

    def resolve_secrets_in(self, container_name, secrets):
        container_info = self.client.inspect_container(container_name)
        container_env = container_info['Config']['Env']
        env = dict()

        for e in container_env:
            key, value = e.split('=', 1)
            env[key] = value

        resolved_secrets = dict()
        for s in secrets or []:
            key = s.upper()
            if key not in env:
                raise ValueError("Secret {} not found in {}".format(key, container_name))
            resolved_secrets[s] = env[key]
        return resolved_secrets

    # noinspection PyMethodMayBeStatic
    def get_port_mapping_in(self, container, port, protocol):
        for p in container['Ports']:
            if p['Type'] == protocol and p['PrivatePort'] == port:
                return p['PublicPort']

        raise ValueError("Port {} was not defined for container {}".format(port, container['Names'][0]))

    def get_container_for(self, service):
        candidates = self.client.containers(filters=dict(
            status='running',
            label='com.docker.compose.service={}'.format(service)
        ))

        if not candidates:
            raise ValueError("No running service found: {}".format(service))

        return candidates[0]


class DnsRegistry(Registry):
    """
    The DNS registry uses DNS lookups for A and CNAMEs. It uses SRV or environment lookups
    to find port numbers.
    """

    def __init__(self):
        self.debug_mode = get_debug_mode(False)

    def register(self, service, port, protocol='tcp', secrets=None):
        port = get_name_by_port(port, protocol)

        try:
            ip = socket.gethostbyname(service)
        except socket.gaierror:
            raise ValueError("Could not resolve service {}".format(service))

        p = self.resolve_port(port, protocol, service)

        resolved_secrets = dict()
        for s in secrets or []:
            secrets_file = '/var/secrets/{}/{}'.format(service, s)
            try:
                with open(secrets_file) as f:
                    resolved_secrets[s] = f.read()
            except OSError:
                raise ValueError("Could not find secrets file {}".format(secrets_file))

        return Service(ip, p, resolved_secrets)

    # noinspection PyMethodMayBeStatic
    def resolve_port(self, port, protocol, service):
        svc = "_{}._{}.{}".format(port, protocol, service)
        try:
            result = dns.resolver.query(svc, "SRV")
            if len(result):
                return result[0].port
        except:
            raise ValueError("Could not resolve service {}".format(svc))

        raise ValueError("Could not find port for service {}".format(svc))


class EnvironmentRegistry(Registry):
    def __init__(self):
        self.debug_mode = get_debug_mode(False)

    def register(self, service, port, protocol="tcp", secrets=None):
        port = get_port_by_name(port, protocol)

        service_key = "{}_PORT_{}_{}_ADDR".format(service.upper(), port, protocol.upper())
        port_key = "{}_PORT_{}_{}_PORT".format(service.upper(), port, protocol.upper())
        env = os.environ

        if service_key not in env:
            raise ValueError("Service {} not found under {}".format(service, service_key))

        if port_key not in env:
            raise ValueError("Port {} not found under {}".format(port, port_key))

        resolved_secrets = dict()
        for s in secrets or []:
            key = "{}_ENV_{}".format(service.upper(), s.upper())
            if key not in env:
                raise ValueError("Secret {} not found under {}".format(s, key))
            resolved_secrets[s] = env[key]

        return Service(env[service_key], int(env[port_key]), resolved_secrets)
