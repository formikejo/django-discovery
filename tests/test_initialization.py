import os
from unittest import TestCase

import discovery
from discovery.registry import DnsRegistry, EnvironmentRegistry, DockerRegistry


class InitializeServicesTest(TestCase):
    def test_discovery_mode_dns(self):
        os.environ['DISCOVERY_MODE'] = 'dns'
        discovery.initialize()

        self.assertIsInstance(discovery.services, DnsRegistry)

    def test_discovery_mode_docker_compose(self):
        os.environ['DISCOVERY_MODE'] = 'env'
        discovery.initialize()

        self.assertIsInstance(discovery.services, EnvironmentRegistry)

    def test_discovery_mode_docker(self):
        os.environ['DISCOVERY_MODE'] = 'docker'
        os.environ['DOCKER_HOST'] = 'tcp://127.0.0.1:1234'
        discovery.initialize()

        self.assertIsInstance(discovery.services, DockerRegistry)

    def test_discovery_mode_is_docker_when_docker_host_is_set(self):
        os.environ['DISCOVERY_MODE'] = ''
        os.environ['DOCKER_HOST'] = 'tcp://127.0.0.1:1234'
        discovery.initialize()

        self.assertIsInstance(discovery.services, DockerRegistry)

    def test_discovery_mode_defaults_to_dns(self):
        os.environ['DISCOVERY_MODE'] = ''
        os.environ['DOCKER_HOST'] = ''
        discovery.initialize()

        self.assertIsInstance(discovery.services, DnsRegistry)

    def test_discovery_mode_docker_fails_if_no_docker_host_is_set(self):
        os.environ['DISCOVERY_MODE'] = 'docker'
        os.environ['DOCKER_HOST'] = ''

        self.assertRaises(ValueError, discovery.initialize)

    def test_error_for_unknown(self):
        os.environ['DISCOVERY_MODE'] = "unknown-mode"
        self.assertRaises(ValueError, discovery.initialize)


class DebugModeTest(TestCase):
    def test_default_for_docker(self):
        r = DockerRegistry(None, None)
        self.assertTrue(r.debug_mode)

    def test_default_for_dns(self):
        r = DnsRegistry()
        self.assertFalse(r.debug_mode)

    def test_default_for_env(self):
        r = EnvironmentRegistry()
        self.assertFalse(r.debug_mode)

    def test_override_for_docker(self):
        os.environ['DISCOVERY_DEBUG'] = "0"
        r = DockerRegistry(None, None)
        self.assertFalse(r.debug_mode)

    def test_override_for_dns(self):
        os.environ['DISCOVERY_DEBUG'] = "1"
        r = DnsRegistry()
        self.assertTrue(r.debug_mode)

    def test_override_for_env(self):
        os.environ['DISCOVERY_DEBUG'] = "1"
        r = EnvironmentRegistry()
        self.assertTrue(r.debug_mode)
