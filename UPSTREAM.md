# Upstream reference

This Rust engine is what MythicSim runs. New work lands here only; community and fork
commits are no longer ported. The pinned Go engine stays as the reference that produced the
accepted Go goldens, which must keep passing.

## The pin

| Source | Role | Revision |
| --- | --- | --- |
| [MythicSim Go fork](https://github.com/sage3648/mythicsim-forever-engine-go) | Reference for the Go goldens and the fixture exporter | `pinned_revision` and `client_build` in [upstream/sources.json](upstream/sources.json) |
| [Community Forever engine](https://github.com/ElliotWood/Forever) | Base of the fork, reviewed in the ledger below | `community_base`, `adopted_base` and `last_reviewed` in the same file |

Go is a reference implementation, not proof of live-game correctness.

[upstream/sources.json](upstream/sources.json) is the only written copy of the pin. Readers:

- `build.rs` sets `FOREVER_REFERENCE_REVISION` and `FOREVER_CLIENT_BUILD` from the
  `reference` source's `pinned_revision` and `client_build`.
- `tools/compare.py` exports `PIN` and `CLIENT_BUILD`, which `tools/prepared_v2.py`,
  `tools/shadow.py` and the other Python tools import. The Go helpers in `tools/oracle` and
  `tools/oracle-v2` receive the pin through `-ldflags -X` (`go_pin_flags`).
- `python3 tools/prepared_v2.py check` rejects a fixture manifest or prepared input whose
  revision or client build differs from the pin.

Fixtures, validation records and benchmark snapshots keep the revision they were made with as
provenance. `tools/matched-go/main.go` writes its accepted revision as a constant, since it
builds without the pin.

## Moving the pin

1. Change `pinned_revision`, `client_build` and, if the fork rebased, `community_base` in
   `upstream/sources.json`.
2. Run `python3 tools/prepared_v2.py repin --output <scratch>`. It re-exports every prepared
   input and Go golden at the new pin and lists each changed golden in `<scratch>/repin.json`.
   Each change is a reference behavior change to review: port it to Rust until
   `python3 tools/prepared_v2.py compare` matches every case, then run `cargo test`.
3. Export on arm64. The accepted goldens come from the exporter built for arm64, whose
   compiler fuses some multiply and add steps that Rust follows with `mul_add`, so an amd64
   build differs in the last bits. `tools/architecture_check.py --goarch arm64` runs the
   pinned exporter for linux/arm64 in Docker and compares every accepted golden.
4. Re-export the Frost kernel fixtures with `tools/compare.py`'s oracle and check they keep
   their values, then move the `revision` constant in `tools/matched-go/main.go` and run its
   `go test ./...`.
5. Update `go_reference.revision` and `client_build` in `release/manifest.json`, re-run the
   recorded sweeps that the move affects, and run `python3 tools/upstream.py check`.

## Ledger

[upstream/](upstream/) also holds the review of the community range the fork was built on:

| File | Content |
| --- | --- |
| [sources.json](upstream/sources.json) | The pin, the adopted community base and the last reviewed community range |
| [changes.json](upstream/changes.json) | Every community commit in the reviewed range, with a disposition and reason; applicable changes carry adoption state and regression fixtures |
| [mechanics-map.json](upstream/mechanics-map.json) | Mechanics with their Go files, Rust modules, tests, status, linked community changes and fork patch numbers |

`tools/upstream.py check` audits them offline: the reference pin equals the comparison pin,
the ledger covers exactly the reviewed range, every change has a known disposition and reason,
applicable changes name existing regression files, the reference's community base is the
adopted base or a reviewed commit, and changes and mechanics link to each other.
`--community /absolute/path/to/Forever` also checks the commit list against a local clone.

```sh
python3 tools/upstream.py check
python3 -m unittest discover -s tools -p 'upstream*_test.py'
```

## Reference defects

Two Go defects are fixed at the pin, and Rust follows the fixed behavior:

- Ignite on the Goblin Sapper Charge's hit on the player: before the fork's patch 88 (later
  93, and community #702), Ignite heard the charge's crit on the Mage and panicked on a nil
  dot. Ignite now requires an enemy target in both engines; `fire-mage-goblin-sapper` is
  accepted with Go goldens.
- A pushback after the hardcast completed: before the fork's patch 89 (later 94, and
  community #701), a pushback handler that ran a batch window after the cast ended pushed
  the finished cast back and it landed twice. The handler now returns when the hardcast
  has ended, as `Fight::pushback_handler` does; `feral-bear-druid-boomerang-pushback-after-cast`
  checks it.

## Reproducing the reference comparison

Requires stable Rust, Go, Python 3, Git and protoc:

```sh
python3 tools/compare.py
python3 tools/fair_compare.py
```

The tools clone the pinned Go source into ignored scratch storage; pass
`--source /absolute/path` for a local repository that contains the commit.
