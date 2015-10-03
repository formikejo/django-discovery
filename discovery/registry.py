class Service(object):
    """
    Models a service.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port


class DockerRegistry(object):
    """
    The docker registry uses a docker-client to connect to docker.
    """

    def __init__(self, client, host):
        self.host = host
        self.using_docker = True
        self.client = client

    def register(self, service, port, protocol='tcp'):
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


class DnsRegistry(object):
    """
    The DNS registry uses DNS lookups for A and CNAMEs. It uses SRV or environment lookups
    to find port numbers.
    """

    def __init__(self):
        self.using_docker = False
