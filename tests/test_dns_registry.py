import socket
from unittest import TestCase
from unittest.mock import patch

import dns
from dns.name import Name
from dns.rdtypes.IN.SRV import SRV
from dns.resolver import NXDOMAIN

from discovery import DnsRegistry


@patch('dns.resolver.query', return_value=[SRV(1, 33, priority=10, weight=100, port=27384, target=Name(['my_db']))])
@patch('socket.gethostbyname', return_value='172.18.0.23')
class DnsRegistryTest(TestCase):
    def setUp(self):
        self.service = 'my_db'
        self.nport = 3306
        self.sport = 'mysql'

        self.service_ip = '172.18.0.23'
        self.service_port = 27384

        self.r = DnsRegistry()

    def test_register_creates_service(self, socket_mock, resolver):
        svc = self.r.register(self.service, self.nport)
        self.assertIsNotNone(svc)

    def test_registered_service_resolves_host(self, socket_mock, resolver):
        svc = self.r.register(self.service, self.nport)
        self.assertEqual(svc.host, self.service_ip)

    def test_registered_service_resolves_port(self, socket_mock, resolver):
        svc = self.r.register(self.service, self.nport)
        self.assertEqual(svc.port, self.service_port)

    def test_register_fails_if_no_service_match(self, socket_mock, resolver):
        socket_mock.side_effect = socket.gaierror()
        self.assertRaises(ValueError, self.r.register, 'service', 'http')

    def test_register_fails_if_no_port_match(self, socket_mock, resolver):
        with patch.object(dns.resolver, 'query', side_effect=NXDOMAIN()):
            self.assertRaises(ValueError, self.r.register, self.service, self.nport)

    def test_register_fails_if_not_protocol_match(self, socket_mock, resolver):
        with patch.object(dns.resolver, 'query', side_effect=NXDOMAIN()):
            self.assertRaises(ValueError, self.r.register, self.service, self.nport, protocol="udp")

    def test_register_resolves_named_ports(self, socket_mock, resolver):
        svc = self.r.register(self.service, self.sport)
        self.assertEqual(svc.port, self.service_port)

    def test_register_fails_on_weird_named_ports(self, socket_mock, resolver):
        with patch.object(dns.resolver, 'query', side_effect=NXDOMAIN()):
            self.assertRaises(ValueError, self.r.register, self.service, 'non-existing-service-port-name')
