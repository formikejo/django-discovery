from unittest import TestCase
from discovery import DnsRegistry


class DnsRegistryTest(TestCase):

    def setUp(self):
        self.r = DnsRegistry()

