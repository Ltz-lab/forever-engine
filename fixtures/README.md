# Frozen prepared-v1 Frostbolt fixtures

The manifest and 11 paired Go/Rust requests are historical synthetic scenarios
for the prepared Frostbolt kernel. They are read by the class/spec integration
tests in [tests/classes/mage/frost/oracle.rs](../tests/classes/mage/frost/oracle.rs).

These files keep their original names, contents and reference identity. The source
layout refactor does not regenerate or relocate accepted fixture evidence. The
[kernel guide](../docs/kernel.md) explains this boundary and unsupported inputs.

The full application Frost reference is separately inventoried under
[inventory/first-frost/](../inventory/first-frost/manifest.json). It is not an input
accepted by the Rust kernel.

The first such family is [mage/prepared-v2](mage/prepared-v2/manifest.json),
accepted [prepared v2](../docs/prepared-v2.md) inputs with their expected coverage.

New fixture families should use `fixtures/<class>/<spec>/<schema-or-reference>/`
with a manifest identifying source, schema and expected coverage. Class tests
should follow the same class/spec names. Introduce a new family when it has real
cases; do not populate placeholder directories for unimplemented classes.

## Compressed files

Large files in `mage/prepared-v2` (`*.prepared.json`, `*.go-result.json` and `*.go-log.txt`)
are stored as `NAME.gz`, made with `gzip -n` so the bytes are reproducible. Manifests and
`upstream/changes.json` keep naming `NAME`, and their digests are of the decompressed bytes.
`frost-reference.prepared.json` stays plain for the README quick start, and requests and
`manifest.json` are never compressed.

Readers use `tests/support/fixtures.rs` in Rust tests and `tools/fixture_files.py` in Python
tools, which fall back to `NAME.gz` when `NAME` is missing. `tools/prepared_v2.py` compresses
what it writes.
