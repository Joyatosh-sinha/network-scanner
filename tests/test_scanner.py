
import unittest
from unittest.mock import patch

from src.scanner import (
    get_service_name,
    identify_service,
    scan_port,
    scan_ports,
)


class TestScanner(unittest.TestCase):

    @patch("src.scanner.socket.socket")
    def test_scan_port_open(self, mock_socket):
        mock_socket.return_value.connect_ex.return_value = 0

        self.assertTrue(scan_port("127.0.0.1", 8000))

    @patch("src.scanner.socket.socket")
    def test_scan_port_closed(self, mock_socket):
        mock_socket.return_value.connect_ex.return_value = 1

        self.assertFalse(scan_port("127.0.0.1", 8001))

    def test_get_service_name(self):
        self.assertEqual(get_service_name(80), "http")

    def test_unknown_service_port(self):
        with patch(
            "src.scanner.socket.getservbyport",
            side_effect=OSError,
        ):
            self.assertEqual(get_service_name(65000), "unknown")

    def test_identify_http_service(self):
        banner = "HTTP/1.0 200 OK"
        self.assertEqual(identify_service(8000, banner), "http")

    def test_identify_ssh_service(self):
        banner = "SSH-2.0-OpenSSH_9.2"
        self.assertEqual(identify_service(22, banner), "ssh")

    def test_identify_ftp_service(self):
        banner = "220 FTP Server Ready"
        self.assertEqual(identify_service(21, banner), "ftp")

    def test_identify_smtp_service(self):
        banner = "220 mail.example.com ESMTP"
        self.assertEqual(identify_service(25, banner), "smtp")

    def test_identify_mysql_service(self):
        banner = "MySQL server version 8.0"
        self.assertEqual(identify_service(3306, banner), "mysql")

    def test_identify_empty_banner_fallback(self):
        with patch(
            "src.scanner.socket.getservbyport",
            return_value="http-alt",
        ):
            self.assertEqual(
                identify_service(8000, None),
                "http-alt",
            )

    @patch("src.scanner.scan_port")
    def test_scan_ports_returns_open_ports(self, mock_scan):
        mock_scan.side_effect = (
            lambda ip, port, timeout: port in (80, 443)
        )

        result = scan_ports(
            "127.0.0.1",
            79,
            444,
            workers=10,
        )

        self.assertEqual(result, [80, 443])

    @patch("src.scanner.scan_port")
    def test_scan_ports_returns_sorted_ports(self, mock_scan):
        mock_scan.side_effect = (
            lambda ip, port, timeout: port in (83, 80, 81)
        )

        result = scan_ports(
            "127.0.0.1",
            80,
            83,
            workers=4,
        )

        self.assertEqual(result, [80, 81, 83])

    def test_scan_ports_rejects_invalid_range(self):
        with self.assertRaises(ValueError):
            scan_ports("127.0.0.1", 100, 50)

    def test_scan_ports_rejects_invalid_workers(self):
        with self.assertRaises(ValueError):
            scan_ports("127.0.0.1", 80, 90, workers=0)

    def test_scan_ports_rejects_non_integer_workers(self):
        with self.assertRaises(TypeError):
            scan_ports("127.0.0.1", 80, 90, workers="ten")


if __name__ == "__main__":
    unittest.main()
