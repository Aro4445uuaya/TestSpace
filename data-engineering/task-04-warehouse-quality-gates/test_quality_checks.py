
import unittest
from unittest.mock import Mock

from quality_checks import run_quality_checks


class TestDataQuality(unittest.TestCase):

    def test_all_checks_pass(self):
        cursor = Mock()
        cursor.fetchone.return_value = (0,)

        run_quality_checks(cursor)

        self.assertEqual(cursor.execute.call_count, 7)

    def test_quality_failure_stops_pipeline(self):
        cursor = Mock()
        cursor.fetchone.side_effect = [
            (0,), (0,), (1,), (0,), (0,), (0,), (0,)
        ]

        with self.assertRaises(ValueError):
            run_quality_checks(cursor)


if __name__ == "__main__":
    unittest.main()
