# Validation summary

What checks the engine today, and the command that runs each check. The checks below run in
CI (see [CONTRIBUTING](../CONTRIBUTING.md#development-checks)) and need no Go toolchain.

## Go goldens

The prepared v2 fixture family, `fixtures/mage/prepared-v2/manifest.json`, lists every
accepted case. Each case holds its request, the prepared state the pinned Go exporter wrote and
its expected coverage; a case with a `go_result` also holds the pinned Go engine's result and
log.

```sh
python3 -c "import json; c = json.load(open('fixtures/mage/prepared-v2/manifest.json'))['cases']; print(len(c), sum(1 for x in c if x.get('go_result')))"
```

| Test | What it checks |
| --- | --- |
| `supported_cases_match_pinned_go_goldens` (`tests/classes/mage/prepared_v2.rs`) | Every case with a `go_result` simulates to Go's result and log |
| `accepted_fixtures_report_their_expected_coverage` (same file) | The gate's verdict on every case |
| `tests/prepare.rs` | Rust preparation of every case's request equals the Go exporter's prepared state |
| `tests/classes/mage/frost/oracle.rs` | The fixed gear Frost scenarios, `fixtures/*.go.json` |

All run under `cargo test --locked`; to run one alone:

```sh
cargo test --locked --test classes supported_cases_match_pinned_go_goldens
```

`python3 tools/prepared_v2.py check` audits the fixture family offline: its manifest, file
digests and exporter identity.

The reference pin and how to move it are in [UPSTREAM.md](../UPSTREAM.md).

## Rust-only mechanics

Mechanics Go never had have no Go golden. Each is pinned by a focused test against the client
rows, tooltips or logs it comes from, listed in
[README, Rust-only mechanics](../README.md#rust-only-mechanics), for example
`tests/healers.rs`, `tests/healer_gear.rs` and `tests/healer_spells.rs`.

## Determinism and routing

`tests/determinism.rs`, `tests/interruption.rs` and `tools/route_test.py` check what
[routing](routing.md) promises: the same input and seed give the same result, and an
interrupted run leaves no partial result.

## Records

`validation/` and `benchmarks/` hold dated records of past comparison runs and benchmarks. They
are history, not checks: nothing in CI reads them, and this page does not depend on any one of
them.
