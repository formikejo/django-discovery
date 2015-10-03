import os
from unittest import TestCase

from discovery import EnvironmentRegistry


class EnvironmentRegistryTest(TestCase):
    def setUp(self):
        self.service = 'my_db'
        self.nport = 3306
        self.sport = 'mysql'

        self.service_ip = '172.18.0.23'
        self.service_port = 27384

        os.environ.update(dict(
            MY_DB_PORT_3306_TCP_ADDR=self.service_ip,
            MY_DB_PORT_3306_TCP_PORT=str(self.service_port)
        ))

        self.r = EnvironmentRegistry()

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