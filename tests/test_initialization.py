import os
from unittest import TestCase

import discovery
import discovery.registry


class InitializeServicesTest(TestCase):

    def test_services_is_docker_registry_when_docker_host_is_set(self):
        os.environ['DOCKER_HOST'] = 'tcp://127.0.0.1:1234'
        discovery.initialize()

        self.assertIsInstance(discovery.services, discovery.registry.DockerRegistry)

    def test_services_is_dns_registry_when_docker_host_is_not_set(self):
        del os.environ['DOCKER_HOST']
        discovery.initialize()

        self.assertIsInstance(discovery.services, discovery.registry.DnsRegistry)
