import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest

import fixture_files


class FixtureFilesTests(unittest.TestCase):
    def test_plain_and_compressed_read_the_same_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            data = b'{"a": 1}\n'
            (directory / "plain.json").write_bytes(data)
            (directory / "packed.json").write_bytes(data)
            packed = fixture_files.store(directory / "packed.json")
            self.assertEqual(packed.name, "packed.json.gz")
            self.assertFalse((directory / "packed.json").exists())
            self.assertEqual(gzip.decompress(packed.read_bytes()), data)
            for name in ("plain.json", "packed.json"):
                path = directory / name
                self.assertTrue(fixture_files.exists(path))
                self.assertEqual(fixture_files.read_bytes(path), data)
                self.assertEqual(fixture_files.load(path), {"a": 1})
                self.assertEqual(fixture_files.digest(path), hashlib.sha256(data).hexdigest())
            self.assertFalse(fixture_files.exists(directory / "missing.json"))

    def test_store_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.go-log.txt"
            path.write_text("line\n" * 100)
            first = fixture_files.store(path).read_bytes()
            path.write_text("line\n" * 100)
            self.assertEqual(fixture_files.store(path).read_bytes(), first)

    def test_materialize_writes_a_real_file_only_when_compressed(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as scratch:
            plain = Path(directory) / "frost-reference.prepared.json"
            plain.write_text("{}")
            self.assertEqual(fixture_files.store(plain), plain)
            self.assertEqual(fixture_files.materialize(plain, scratch), plain)
            packed = Path(directory) / "case.prepared.json"
            packed.write_text("{}")
            fixture_files.store(packed)
            copy = fixture_files.materialize(packed, scratch)
            self.assertEqual(copy, Path(scratch) / "case.prepared.json")
            self.assertEqual(copy.read_text(), "{}")


if __name__ == "__main__":
    unittest.main()
