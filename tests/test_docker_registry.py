from unittest import TestCase
from unittest.mock import MagicMock

import docker

from discovery import DockerRegistry


class DockerRegistryTest(TestCase):
    def setUp(self):
        self.service = 'my_db'
        self.service_ip = '172.18.0.23'

        self.nport = 3306
        self.sport = 'mysql'
        self.service_port = 27384

        self.secret = 'my_secret'
        self.secret_value = 'my_value'

        self.client = docker.Client()
        self.client.containers = MagicMock(return_value=[
            dict(
                Ports=[
                    dict(Type="tcp", PrivatePort=self.nport, PublicPort=self.service_port)
                ],
                Names=['mock-container']
            )
        ])
        self.client.inspect_container = MagicMock(return_value = dict(
            Config=dict(
                Env=dict(
                    MY_SECRET=self.secret_value
                )
            )
        ))
        self.r = DockerRegistry(self.client, self.service_ip)

    def test_register_creates_service(self):
        svc = self.r.register(self.service, self.nport)
        self.assertIsNotNone(svc)

    def test_registered_service_resolves_host(self):
        svc = self.r.register(self.service, self.nport)
        self.assertEqual(svc.host, self.service_ip)

    def test_registered_service_resolves_port(self):
        svc = self.r.register(self.service, self.nport)
        self.assertEqual(svc.port, self.service_port)

    def test_register_fails_if_no_service_match(self):
        self.client.containers = MagicMock(return_value=[])
        self.assertRaises(ValueError, self.r.register, 'service', 'http')

    def test_register_fails_if_no_port_match(self):
        self.assertRaises(ValueError, self.r.register, self.service, self.nport + 1)

    def test_register_fails_if_not_protocol_match(self):
        self.assertRaises(ValueError, self.r.register, self.service, self.nport, protocol="udp")

    def test_register_resolves_named_ports(self):
        svc = self.r.register(self.service, self.sport)
        self.assertEqual(svc.port, self.service_port)

    def test_register_fails_on_weird_named_ports(self):
        self.assertRaises(ValueError, self.r.register, self.service, 'non-existing-service-port-name')

    def test_service_secret_resolves_secret(self):
        svc = self.r.register(self.service, self.nport, secrets=[self.secret])
        self.assertEquals(svc.secrets[self.secret], self.secret_value)

    def test_register_fails_on_missing_service_secret(self):
        self.assertRaises(ValueError, self.r.register, self.service, self.nport, secrets=['unknown-secret'])
