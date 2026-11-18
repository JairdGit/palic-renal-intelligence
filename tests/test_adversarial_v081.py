import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from src.integrity.manifest import verify_release_manifest


def write_manifest(root, payload):
    (root / "RELEASE_MANIFEST.json").write_text(json.dumps(payload), encoding="utf-8")


class ManifestHardeningTests(unittest.TestCase):
    def test_non_object_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "RELEASE_MANIFEST.json").write_text("[]", encoding="utf-8")
            self.assertEqual(verify_release_manifest(root)["status"], "INVALID_MANIFEST")

    def test_duplicate_json_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "RELEASE_MANIFEST.json").write_text('{"file_sha256":{},"file_sha256":{"x":"' + '0'*64 + '"}}', encoding="utf-8")
            self.assertEqual(verify_release_manifest(root)["status"], "INVALID_MANIFEST")

    def test_malformed_digest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.txt").write_text("x", encoding="utf-8")
            write_manifest(root, {"file_sha256":{"sample.txt":"not-a-sha256"}})
            result = verify_release_manifest(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["failed"], ["sample.txt"])

    def test_parent_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(root, {"file_sha256":{"../outside.txt":"0"*64}})
            self.assertEqual(verify_release_manifest(root)["failed"], ["../outside.txt"])

    def test_absolute_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(root, {"file_sha256":{str(root / 'x.txt'):'0'*64}})
            self.assertEqual(verify_release_manifest(root)["failed"], [str(root / 'x.txt')])

    def test_valid_manifest_still_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = b"release-file"
            (root / "sample.txt").write_bytes(content)
            write_manifest(root, {"file_sha256":{"sample.txt":hashlib.sha256(content).hexdigest()}})
            self.assertEqual(verify_release_manifest(root)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
