
import unittest
from unittest.mock import patch

from src.utils import resolve_target


class TestUtils(unittest.TestCase):

    @patch("src.utils.socket.gethostbyname")
    def test_resolve_hostname(self, mock_resolve):
        mock_resolve.return_value = "127.0.0.1"

        self.assertEqual(
            resolve_target("localhost"),
            "127.0.0.1",
        )

    @patch(
        "src.utils.socket.gethostbyname",
        side_effect=OSError("Name resolution failed"),
    )
    def test_invalid_hostname(self, mock_resolve):
        with self.assertRaises(ValueError):
            resolve_target("invalid-hostname-for-testing.invalid")


if __name__ == "__main__":
    unittest.main()
