# Forever Engine

A Rust simulation engine for WoW Forever, used by [MythicSim](https://mythicsim.com/wow-forever/sim).
It prepares characters, checks coverage and simulates fights. Go goldens remain a regression
check for the behavior they cover; new mechanics can be tested independently of Go.

## Quick start

Install stable Rust, then run:

```sh
git clone https://github.com/Ltz-lab/forever-engine.git
cd forever-engine
cargo run --locked --release -- check --infile fixtures/mage/prepared-v2/frost-reference.prepared.json
cargo run --locked --release -- sim --infile fixtures/mage/prepared-v2/frost-reference.prepared.json
```

`check` reports coverage for a prepared input. `sim` prints the result JSON. For application
requests, use `sim --request REQUEST.json --gate`; see [routing](docs/routing.md).

## How it works

1. [Preparation](docs/rust-preparation.md) turns a request into a [prepared v2](docs/prepared-v2.md)
   character and encounter.
2. The coverage gate reports unsupported input with reason codes.
3. The shared fight runtime runs supported inputs and produces metrics and logs.

The [routing tool](docs/routing.md) runs these stages for worker requests. It can optionally
fall back to Go; its documentation explains the configuration and refusal behavior.

## Coverage

Class agents cover Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock and Warrior,
including damage, tank and healer builds. Supported inputs include talents, gear, buffs,
consumables, pets, item swaps and multiple targets. The gate checks each prepared input rather
than guaranteeing that every combination is supported. See [prepared v2](docs/prepared-v2.md)
and the [validation summary](docs/validation-summary.md) for coverage and fixture checks.

Holy Paladin heals can be compared under Go reference rules, which count heals in full. Forever
preparation accounts for overhealing. A Quick Sim timeline and combat log show the first fight,
not a median iteration.

## Rust-only mechanics

Mechanics the Go engine never had have no Go golden. They are checked against the game's own
numbers instead: client spell rows, Wowhead Forever tooltips and logs, with focused tests that
pin the expected heal, cost or timing. Where Rust departs from a mechanic the Go reference has,
preparation follows Forever by default and the reference with `Rules::GoReference`
(`prepare --go-rules`), which every comparison with the Go goldens uses.
[Rust-only mechanics](docs/rust-only-mechanics.md) lists each one with its evidence.

## Checks

```sh
cargo test --locked
cargo fmt -- --check
cargo clippy --locked --all-targets -- -D warnings
python3 -m unittest discover -s tools -p '*_test.py'
python3 tools/prepared_v2.py check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full CI checks, including WebAssembly and Go
tooling, and [validation](docs/validation-summary.md) for what the tests cover.

## Documentation

- [Contributor code map](docs/contributor-guide.md) and [contributing](CONTRIBUTING.md)
- [Prepared v2 contract](docs/prepared-v2.md), [preparation](docs/rust-preparation.md), and
  [routing](docs/routing.md)
- [Chance on hit items](docs/forever-chance-on-hit.md), [reference pin](UPSTREAM.md), and
  [roadmap](ROADMAP.md)

The project is MIT licensed; see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md) for provenance.
