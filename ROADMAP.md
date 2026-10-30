# Roadmap

Forever Engine runs every Forever sim on MythicSim (see [README](README.md#coverage)). New
Forever work lands here only. The Go goldens stay as a regression guard on what Go covered;
nothing is ported from upstream.

Open work is on the [contributor board](https://github.com/Ltz-lab/forever-engine/issues/25),
which `python3 tools/board.py update` builds from the issues.

## Next

- Close the coverage gaps the gate still refuses. Each refusal has a stable code
  ([routing](docs/routing.md)); a gap without an issue shows on the board.
- Recalibrate the healer overheal shares and the party damage rates once Forever's logs cover
  level 60 raids, Prayer of Mending and Chain Heal
  ([Rust-only mechanics](README.md#rust-only-mechanics)).
- Move the racial and class rows that come from Forever's development notes onto client data
  once a client build carries them.
- Model mechanics Go never had against the client rows, tooltips and logs, each with a focused
  test that pins its numbers.

## Rules that stay

- Every accepted Go golden keeps passing (`cargo test --locked`). A change that moves one has to
  explain why the reference no longer applies.
- The coverage gate refuses what Rust cannot simulate exactly, with a reason code.
- Results stay deterministic for a given input and seed.
