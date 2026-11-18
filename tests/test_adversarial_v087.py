import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import pandas as pd

from src.io_safety.safe_io import (
    ArtifactReadError, publish_directory_transactionally,
    read_csv_checked, read_json_checked,
)


class SafeArtifactIOV087(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_csv_fails_closed(self):
        with self.assertRaises(ArtifactReadError):
            read_csv_checked(self.root / 'missing.csv', required_columns=['id'])

    def test_empty_csv_fails_closed(self):
        p = self.root / 'empty.csv'; p.write_text('', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_csv_checked(p, required_columns=['id'])

    def test_malformed_csv_fails_closed(self):
        p = self.root / 'bad.csv'; p.write_text('id,value\n1,2\n3,4,5\n', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_csv_checked(p, required_columns=['id', 'value'])

    def test_missing_required_column_fails_closed(self):
        p = self.root / 'schema.csv'; p.write_text('id\n1\n', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_csv_checked(p, required_columns=['id', 'value'])

    def test_invalid_date_fails_closed(self):
        p = self.root / 'date.csv'; p.write_text('id,date\n1,not-a-date\n', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_csv_checked(p, required_columns=['id', 'date'], date_columns=['date'])

    def test_duplicate_json_keys_fail_closed(self):
        p = self.root / 'duplicate.json'; p.write_text('{"version":"a","version":"b"}', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_json_checked(p)

    def test_json_non_object_root_fails_closed(self):
        p = self.root / 'array.json'; p.write_text('[1,2]', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_json_checked(p)

    def test_json_nan_fails_closed(self):
        p = self.root / 'nan.json'; p.write_text('{"metric":NaN}', encoding='utf-8')
        with self.assertRaises(ArtifactReadError):
            read_json_checked(p)

    def test_transaction_replaces_complete_directory(self):
        destination = self.root / 'generated'
        destination.mkdir(); (destination / 'old.txt').write_text('old')
        staging = self.root / '.staging'; staging.mkdir(); (staging / 'new.txt').write_text('new')
        publish_directory_transactionally(staging, destination)
        self.assertFalse((destination / 'old.txt').exists())
        self.assertEqual((destination / 'new.txt').read_text(), 'new')
        self.assertFalse((self.root / 'generated.previous').exists())


    def test_transaction_restores_previous_output_when_promotion_fails(self):
        destination = self.root / 'generated'
        destination.mkdir(); (destination / 'old.txt').write_text('old')
        staging = self.root / '.staging'; staging.mkdir(); (staging / 'new.txt').write_text('new')
        import src.io_safety.safe_io as safe_io
        real_replace = safe_io.os.replace
        calls = {'n': 0}
        def flaky_replace(src, dst):
            calls['n'] += 1
            if calls['n'] == 2:
                raise OSError('simulated promotion failure')
            return real_replace(src, dst)
        with mock.patch.object(safe_io.os, 'replace', side_effect=flaky_replace):
            with self.assertRaises(OSError):
                publish_directory_transactionally(staging, destination)
        self.assertEqual((destination / 'old.txt').read_text(), 'old')
        self.assertFalse((destination / 'new.txt').exists())

    def test_transaction_requires_same_parent(self):
        staging = self.root / 'stage'; staging.mkdir()
        other = self.root / 'sub'; other.mkdir()
        with self.assertRaises(ValueError):
            publish_directory_transactionally(staging, other / 'destination')


if __name__ == '__main__':
    unittest.main()
