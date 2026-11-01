import unittest
from unittest.mock import patch

from src.utils import resolve_target


class TestResolveTarget(unittest.TestCase):

    @patch("src.utils.socket.gethostbyname")
    def test_resolve_hostname(self, mock_resolve):
        mock_resolve.return_value = "127.0.0.1"

        result = resolve_target("localhost")

        self.assertEqual(result, "127.0.0.1")

    def test_reject_empty_target(self):
        with self.assertRaises(ValueError):
            resolve_target("")

    def test_reject_whitespace_target(self):
        with self.assertRaises(ValueError):
            resolve_target("   ")

    def test_reject_non_string_target(self):
        with self.assertRaises(ValueError):
            resolve_target(None)

    @patch("src.utils.socket.gethostbyname")
    def test_strip_target_whitespace(self, mock_resolve):
        mock_resolve.return_value = "127.0.0.1"

        result = resolve_target(" localhost ")

        self.assertEqual(result, "127.0.0.1")
        mock_resolve.assert_called_once_with("localhost")

    @patch(
        "src.utils.socket.gethostbyname",
        side_effect=OSError("Network error"),
    )
    def test_unresolvable_target(self, mock_resolve):
        with self.assertRaises(ValueError):
            resolve_target("invalid.example")

        mock_resolve.assert_called_once()


if __name__ == "__main__":
    unittest.main()