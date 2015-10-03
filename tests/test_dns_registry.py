from unittest import TestCase
from discovery import DnsRegistry


class DnsRegistryTest(TestCase):

    def setUp(self):
        self.r = DnsRegistry()

    def test_uses_docker_is_false(self):
        self.assertFalse(self.r.using_docker)
