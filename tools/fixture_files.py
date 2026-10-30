"""Accepted fixtures, read whether they are stored plain or gzip-compressed.

The large prepared v2 fixtures are kept on disk as NAME.gz, written by `gzip -n` so the
bytes are reproducible. Manifests and ledgers still name NAME, and every accepted digest is
of the uncompressed bytes. These helpers read NAME when it exists and otherwise decompress
NAME.gz; `store` compresses a freshly written fixture the same way.
"""

import gzip
import hashlib
import json
from pathlib import Path
import subprocess

SUFFIX = ".gz"
# Kept plain: the README quick start passes it straight to the engine.
PLAIN = frozenset({"frost-reference.prepared.json"})


def stored(path):
    """The file on disk holding `path`: itself, else its gzip copy. A missing file is `path`."""
    path = Path(path)
    if path.is_file():
        return path
    packed = path.with_name(path.name + SUFFIX)
    return packed if packed.is_file() else path


def exists(path):
    return stored(path).is_file()


def read_bytes(path):
    """The uncompressed bytes of `path`."""
    source = stored(path)
    data = source.read_bytes()
    return gzip.decompress(data) if source != Path(path) else data


def read_text(path):
    return read_bytes(path).decode("utf-8")


def load(path):
    return json.loads(read_bytes(path))


def digest(path):
    """SHA-256 of the uncompressed bytes, the digest manifests record."""
    return hashlib.sha256(read_bytes(path)).hexdigest()


def materialize(path, directory):
    """A real file holding the bytes of `path`, for a command that opens it itself: `path`
    when it is stored plain, else a copy decompressed into `directory`."""
    path = Path(path)
    if path.is_file():
        return path
    target = Path(directory) / path.name
    target.write_bytes(read_bytes(path))
    return target


def store(path):
    """Compress a freshly written fixture in place with `gzip -n`, replacing any earlier
    copy, unless it is one kept plain. Returns the file on disk."""
    path = Path(path)
    if path.name in PLAIN:
        return path
    subprocess.run(["gzip", "-n", "-f", str(path)], check=True)
    return path.with_name(path.name + SUFFIX)
