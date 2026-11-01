
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import (
    create_report_data,
    save_csv_report,
    save_json_report,
    save_results,
    save_text_report,
)


class TestReportData(unittest.TestCase):

    def setUp(self):
        self.open_ports = [
            {
                "port": 8000,
                "service": "http",
                "banner": "HTTP/1.0 200 OK",
            },
            {
                "port": 22,
                "service": "ssh",
                "banner": "SSH-2.0-OpenSSH",
            },
        ]

    def test_create_report_data(self):
        report = create_report_data(
            "localhost",
            "127.0.0.1",
            1,
            1000,
            self.open_ports,
        )

        self.assertEqual(report["target"], "localhost")
        self.assertEqual(report["ip_address"], "127.0.0.1")
        self.assertEqual(report["port_range"]["start"], 1)
        self.assertEqual(report["port_range"]["end"], 1000)
        self.assertEqual(report["total_open_ports"], 2)
        self.assertEqual(report["open_ports"], self.open_ports)
        self.assertIn("scan_date", report)

    def test_create_report_data_with_no_open_ports(self):
        report = create_report_data(
            "127.0.0.1",
            "127.0.0.1",
            1,
            100,
            [],
        )

        self.assertEqual(report["total_open_ports"], 0)
        self.assertEqual(report["open_ports"], [])


class TestReportExports(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.results_dir = Path(self.temp_dir.name) / "results"

        self.report = {
            "scan_date": "2026-11-02T00:00:00+05:30",
            "target": "localhost",
            "ip_address": "127.0.0.1",
            "port_range": {
                "start": 7999,
                "end": 8001,
            },
            "total_open_ports": 1,
            "open_ports": [
                {
                    "port": 8000,
                    "service": "http",
                    "banner": "HTTP/1.0 200 OK",
                }
            ],
        }

        self.directory_patch = patch(
            "main.Path",
            side_effect=self.make_test_path,
        )
        self.directory_patch.start()

    def make_test_path(self, path):
        if path == "results":
            return self.results_dir

        return Path(path)

    def tearDown(self):
        self.directory_patch.stop()
        self.temp_dir.cleanup()

    def test_save_text_report(self):
        save_text_report(self.report)

        report_path = self.results_dir / "scan_results.txt"

        self.assertTrue(report_path.exists())

        content = report_path.read_text(encoding="utf-8")

        self.assertIn("NETWORK SCAN REPORT", content)
        self.assertIn("localhost", content)
        self.assertIn("Port 8000", content)
        self.assertIn("HTTP/1.0 200 OK", content)

    def test_save_csv_report(self):
        save_csv_report(self.report)

        csv_files = list(self.results_dir.glob("*.csv"))

        self.assertEqual(len(csv_files), 1)

        with csv_files[0].open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["target"], "localhost")
        self.assertEqual(rows[0]["port"], "8000")
        self.assertEqual(rows[0]["service"], "http")
        self.assertEqual(rows[0]["banner"], "HTTP/1.0 200 OK")

    def test_save_json_report(self):
        save_json_report(self.report)

        json_files = list(self.results_dir.glob("*.json"))

        self.assertEqual(len(json_files), 1)

        with json_files[0].open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.assertEqual(data["target"], "localhost")
        self.assertEqual(data["ip_address"], "127.0.0.1")
        self.assertEqual(data["total_open_ports"], 1)
        self.assertEqual(data["open_ports"][0]["port"], 8000)

    def test_csv_export_with_no_open_ports(self):
        empty_report = self.report.copy()
        empty_report["open_ports"] = []
        empty_report["total_open_ports"] = 0

        save_csv_report(empty_report)

        csv_files = list(self.results_dir.glob("*.csv"))

        self.assertEqual(len(csv_files), 1)

        with csv_files[0].open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        self.assertEqual(rows, [])

    def test_json_export_with_no_open_ports(self):
        empty_report = self.report.copy()
        empty_report["open_ports"] = []
        empty_report["total_open_ports"] = 0

        save_json_report(empty_report)

        json_files = list(self.results_dir.glob("*.json"))

        self.assertEqual(len(json_files), 1)

        with json_files[0].open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.assertEqual(data["total_open_ports"], 0)
        self.assertEqual(data["open_ports"], [])

    def test_save_results_selects_csv(self):
        with patch("main.save_csv_report") as mock_save:
            save_results(self.report, "csv")

        mock_save.assert_called_once_with(self.report)

    def test_save_results_selects_json(self):
        with patch("main.save_json_report") as mock_save:
            save_results(self.report, "json")

        mock_save.assert_called_once_with(self.report)

    def test_save_results_selects_txt(self):
        with patch("main.save_text_report") as mock_save:
            save_results(self.report, "txt")

        mock_save.assert_called_once_with(self.report)

    def test_save_results_rejects_unsupported_format(self):
        with self.assertRaises(ValueError):
            save_results(self.report, "xml")


if __name__ == "__main__":
    unittest.main()
