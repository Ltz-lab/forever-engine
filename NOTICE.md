# Provenance and acknowledgements

## Licensing

The project is MIT licensed. Upstream wowsims copyright and permission notices are retained
in [LICENSE](LICENSE) under the standard MIT terms.

## Simulation lineage

RNG behavior, combat timing and the comparison reference derive from the MIT licensed
wowsims lineage, [ElliotWood/Forever](https://github.com/ElliotWood/Forever) and its
MythicSim Go fork
([sage3648/mythicsim-forever-engine-go](https://github.com/sage3648/mythicsim-forever-engine-go)).
Matching that behavior is the point of the engine: its committed Go goldens gate every
mechanic the Go engine covers.

Fixtures use synthetic characters against client build `1.60.1.70425` at reference revision
`a667dce8492bd9fb94269a9f864289cb74006775`. Historical reports and snapshots keep the original
experiment's date, compiler settings and source digest; extracting them does not constitute a
new timing measurement.

Spell and item identities, mechanic notes and report semantics come from the client's spell
rows, Wowhead Forever tooltips and observed logs.
