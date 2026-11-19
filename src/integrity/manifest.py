from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

MANIFEST_NAME = "RELEASE_MANIFEST.json"
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Clave JSON duplicada: {key}")
        result[key] = value
    return result


_IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv"}
_IGNORED_SUFFIXES = {".pyc", ".pyo"}
# Streamlit injects this runtime-only file when app secrets are configured.
# It must never be committed to the public repository or included in the release manifest.
_IGNORED_RUNTIME_FILES = {".streamlit/secrets.toml"}


def verify_release_manifest(root: str | Path, *, strict: bool = False,
                             expected_version: str | None = None) -> dict:
    """Verify SHA-256 entries; strict mode also enforces complete file inventory.

    The manifest itself is excluded from its own hash list. Runtime caches and
    bytecode are ignored; every other regular release file must be declared.
    Symlinks are rejected in strict mode to avoid ambiguous package contents.
    """
    root = Path(root).resolve()
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"status": "MISSING_MANIFEST", "verified": 0, "failed": [], "missing": []}
    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "INVALID_MANIFEST", "verified": 0, "failed": [], "missing": [str(exc)]}

    if not isinstance(manifest, dict):
        return {"status": "INVALID_MANIFEST", "verified": 0, "failed": [], "missing": ["La raíz del manifiesto debe ser un objeto JSON"]}
    expected = manifest.get("file_sha256")
    if not isinstance(expected, dict) or not expected:
        return {"status": "INVALID_MANIFEST", "verified": 0, "failed": [], "missing": ["file_sha256 ausente o vacío"], "unlisted": []}
    if strict:
        version = manifest.get("version")
        if not isinstance(version, str) or not version:
            return {"status": "INVALID_MANIFEST", "verified": 0, "failed": ["version"], "missing": [], "unlisted": []}
        if expected_version is not None and version != expected_version:
            return {"status": "VERSION_MISMATCH", "verified": 0, "failed": [f"version:{version}!={expected_version}"], "missing": [], "unlisted": []}

    verified, failed, missing = 0, [], []
    for relative, digest in sorted(expected.items(), key=lambda item: str(item[0])):
        # The manifest uses portable POSIX-relative paths only.
        if (not isinstance(relative, str) or not relative or "\\" in relative
                or "\x00" in relative or not isinstance(digest, str)
                or not _SHA256_RE.fullmatch(digest)):
            failed.append(str(relative))
            continue
        rel_path = PurePosixPath(relative)
        if rel_path.is_absolute() or any(part in ("", ".", "..") for part in rel_path.parts):
            failed.append(relative)
            continue
        unresolved = root / Path(*rel_path.parts)
        if strict and any((root / Path(*rel_path.parts[:i])).is_symlink() for i in range(1, len(rel_path.parts) + 1)):
            failed.append(relative)
            continue
        candidate = unresolved.resolve()
        if root not in candidate.parents or candidate == root:
            failed.append(relative)
            continue
        try:
            if not candidate.is_file():
                missing.append(relative)
                continue
            actual = sha256_file(candidate)
        except OSError:
            missing.append(relative)
            continue
        if actual.lower() != digest.lower():
            failed.append(relative)
        else:
            verified += 1

    unlisted = []
    if strict:
        for path in root.rglob("*"):
            if not path.is_file() and not path.is_symlink():
                continue
            rel = path.relative_to(root)
            if (any(part in _IGNORED_DIRS for part in rel.parts)
                    or path.suffix.lower() in _IGNORED_SUFFIXES
                    or rel.as_posix() in _IGNORED_RUNTIME_FILES):
                continue
            relative = rel.as_posix()
            if relative == MANIFEST_NAME:
                continue
            if path.is_symlink() or relative not in expected:
                unlisted.append(relative)
    status = "PASS" if not failed and not missing and not unlisted else "FAIL"
    return {"status": status, "verified": verified, "failed": failed, "missing": missing, "unlisted": sorted(unlisted)}
