
import unittest
from unittest.mock import patch

from src.scanner import scan_port, get_service_name


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


if __name__ == "__main__":
    unittest.main()
