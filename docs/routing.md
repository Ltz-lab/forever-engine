# Routing requests to Rust

`tools/route.py` is the command the MythicSim worker runs for a request. It runs from a bundle
that [`tools/shadow.py build`](shadow-sims.md#build-a-bundle) makes, which holds the engine and
exporter binaries, so the worker needs only Python 3.

```sh
python3 BUNDLE/tools/route.py --request REQUEST.json --output NEW_FOLDER
```

For one request, one engine process (`forever-engine sim --request ... --gate`) prepares the
request, checks it with the coverage gate and simulates it when the gate supports it. When Rust
preparation does not cover the request, the pinned Go exporter prepares it and Rust gates and
runs that, unless Go is off.

## FOREVER_GO_FALLBACK

`FOREVER_GO_FALLBACK` is the worker's switch, read from the environment. Set to `0`, `false`,
`off` or `no` (any case), no Go step runs: a Rust preparation refusal becomes a `fallback`
decision with its code, and the worker fails the request with that reason. MythicSim runs with
it off. Unset or any other value lets the Go exporter prepare what Rust preparation refuses.
`--go-prepare` always prepares with the Go exporter.

## Options

| Option | Meaning |
| --- | --- |
| `--request` | The `RaidSimRequest` JSON |
| `--batch` | Instead of `--request`, the requests of one batch job; see [batch jobs](#batch-jobs) |
| `--output` | A folder that does not exist yet; everything is written there |
| `--bundle` | The bundle folder; by default the one holding the tool |
| `--seed` | The seed for a request without one, 1 to 2^62; by default a fresh one |
| `--timeout` | Seconds each step may take, 300 by default |
| `--go-prepare` | Prepare with the Go exporter even when Rust preparation covers the request |

## Decisions

The command prints one JSON decision and writes it to `NEW_FOLDER/decision.json`.

| `status` | Meaning | Exit status |
| --- | --- | --- |
| `rust` | Rust ran the request. `result` names `NEW_FOLDER/result.json`, its `RaidSimResult`, with the rotation line checks of `sim --rotation-stats`; `identity` names the engine | 0 |
| `fallback` | The gate refused the input, or with Go off Rust preparation did. `refusals` lists each reason with its code, `codes` the distinct codes. No result is written | 0 |
| `fault` | A step failed. `stage` names it (`request`, `rust_prepare`, `prepare`, `check` or `rust`) and `error` says what failed. No result is written | 2 |

A fault is anything that is not a decision: an unreadable request, a step that exits with an
error, is killed or outlives its timeout, unreadable gate output, a refusal without a reason,
or a result without `raidMetrics` or `iterationsDone`. A fault is never counted as a fallback.

Every decision also carries:

- `preparation`: `provider` (`rust` or `go`), and when Rust preparation refused, its `code` and
  `reason`.
- `seed` and `seed_source` (`request`, `argument` or `drawn`). A request keeps its own seed; the
  recorded seed repeats the run exactly.
- `timings_ms`: wall time per step. `rust` is the one engine process; it becomes `check` when
  the gate refused and `rust_prepare` when Rust preparation refused. `prepare` is the Go
  exporter.
- `bundle`: the bundle's `manifest.json`, when it has one.

Refusal codes are listed in the
[prepared v2 contract](prepared-v2.md#unknown-and-unsupported-input).

## Batch jobs

Best Gear, stat weights and rankings run every request of a job in one engine, so differences
between candidates never come from two engines:

```sh
python3 BUNDLE/tools/route.py --batch CANDIDATE.json ... --output NEW_FOLDER
```

Each request is prepared (`rust_prepare`, or `prepare` by the Go exporter) and gated (`check`)
before any runs, and Rust runs only when the gate supports all of them. Each request writes into
`NEW_FOLDER/000`, `001` and so on, and `requests` lists each with its own status.

| `status` | Meaning | Exit status |
| --- | --- | --- |
| `rust` | Every request ran in Rust; each entry names its `result` | 0 |
| `fallback` | At least one request was refused; its entry carries `refusals`, and `codes` gathers all codes. Rust ran none | 0 |
| `fault` | A step failed for at least one request, whose entry names `stage` and `error`. Results already written are deleted and marked `discarded` | 2 |

Requests without their own seed share one seed, `--seed` or one drawn for the batch.

A request with `simOptions.saveAllValues` gets every iteration's value in each distribution's
`allValues`, in iteration order, so stat weights can compare runs iteration by iteration.

## Determinism and interrupted runs

The same input and seed give the same result. A request runs on one thread; iteration `i`
reseeds from the seed plus `i`, and only `elapsed_ns` and `result.elapsedNs` differ between
runs. `tests/determinism.rs` checks this across worker counts, orders and concurrent processes.

The engine has no timeout of its own; `route.py` ends a step that outlives `--timeout`.

- `forever-engine sim --outfile PATH` writes the report to a hidden sibling file and renames it
  over `PATH` only after the simulation succeeds. A killed run leaves `PATH` absent or as it
  was, and at most a `.PATH.<pid>.tmp` sibling.
- After a `rust` fault, `route.py` removes the report and its temporary files. It writes
  `result.json` and `decision.json` by rename, so a `result.json` next to status `rust` is
  complete.

`tests/interruption.rs` and `tools/route_test.py` check this.

The cost of a routed job against Go is measured in
[benchmarks/2026-10-07-whole-jobs-rust-preparation.json](../benchmarks/2026-10-07-whole-jobs-rust-preparation.json).
