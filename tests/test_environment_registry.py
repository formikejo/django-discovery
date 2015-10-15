import os
from unittest import TestCase

from discovery import EnvironmentRegistry


class EnvironmentRegistryTest(TestCase):
    def setUp(self):
        self.service = 'my_db'
        self.service_ip = '172.18.0.23'

        self.nport = 3306
        self.sport = 'mysql'
        self.service_port = 27384

        self.secret = 'my_secret'
        self.secret_value = 'value'

        os.environ.update(dict(
            MY_DB_PORT_3306_TCP_ADDR=self.service_ip,
            MY_DB_PORT_3306_TCP_PORT=str(self.service_port),
            MY_DB_ENV_MY_SECRET=self.secret_value,
        ))

        self.r = EnvironmentRegistry()

    def test_register_creates_service(self):
        svc = self.r.register(self.service, self.nport, self.sport)
        self.assertIsNotNone(svc)

    def test_registered_service_resolves_host(self):
        svc = self.r.register(self.service, self.nport, self.sport)
        self.assertEqual(svc.host, self.service_ip)

    def test_registered_service_resolves_port(self):
        svc = self.r.register(self.service, self.nport, self.sport)
        self.assertEqual(svc.port, self.service_port)

    def test_register_fails_if_no_service_match(self):
        self.assertRaises(ValueError, self.r.register, 'service', 8000, 'http')

    def test_register_fails_if_no_port_match(self):
        self.assertRaises(ValueError, self.r.register, self.service, self.nport + 1, self.sport)

    def test_register_fails_if_not_protocol_match(self):
        self.assertRaises(ValueError, self.r.register, self.service, self.nport, self.sport, protocol="udp")

    def test_register_resolves_named_ports(self):
        svc = self.r.register(self.service, self.nport, self.sport)
        self.assertEqual(svc.port, self.service_port)

    def test_service_secret_resolves_secret(self):
        svc = self.r.register(self.service, self.nport, self.sport, secrets=[self.secret])
        self.assertEquals(svc.secrets[self.secret], self.secret_value)

    def test_register_fails_on_missing_service_secret(self):
        self.assertRaises(ValueError, self.r.register, self.service, self.nport, self.sport, secrets=['unknown-secret'])
