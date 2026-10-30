# Release and rollback

A Rust engine release is a bundle that the MythicSim worker runs: the release Rust engine, the
Go exporter at the reference pin, the comparison and routing tools, and a `manifest.json` naming
every revision. Rust serves every Forever sim. A request Rust refuses fails with its reason while
the worker's [`FOREVER_GO_FALLBACK`](routing.md#forever_go_fallback) is off, as on MythicSim. The
application side, its settings and its logs, is documented in the MythicSim repository.

## Make a release

1. **Start from a green `main`.** CI passes, including the production architecture check.
   Locally, the checks in [CONTRIBUTING.md](../CONTRIBUTING.md#development-checks) pass.
2. **Match the production engine.** The pin in [upstream/sources.json](../upstream/sources.json)
   must equal the application's `FOREVER_SHA`. The worker refuses to route while they
   differ. If production moved, move the pin first, following [UPSTREAM.md](../UPSTREAM.md).
3. **Update the release manifest.** [release/manifest.json](../release/manifest.json) names
   the Go reference revision, the community base, the client build, the Go database digest,
   the contracts and the capabilities with their evidence. Each must agree with the pin and
   the validation records of this commit; `python3 tools/prepared_v2.py check` rejects
   fixtures whose revision or client build differs.
4. **Tag the commit** `bundle-<short-sha>` with an annotated tag, so a release can always
   be rebuilt from its source.
5. **Build the bundle** on the worker machine, from a clean checkout of the tagged commit:

   ```sh
   python3 tools/shadow.py build --output ~/forever-shadow/bundle-<short-sha>
   ```

   The bundle's `manifest.json` records `rust_dirty`; a release bundle must have it false.
6. **Smoke test the bundle** before any worker uses it. Run a supported fixture request and
   a refused one through the bundle's own tools, and check the decisions:

   ```sh
   python3 ~/forever-shadow/bundle-<short-sha>/tools/route.py --request REQUEST.json --output /tmp/smoke-route
   ```

   The supported decision must be `rust`, the refused one `fallback` with its codes. The
   decision's `bundle` must name the tagged commit in `rust_revision`, and the result's
   `identity` the pin and the client build.

To compare a bundle with Go before it serves users, use [shadow runs](shadow-sims.md).

## Observe a release

- **Routing decisions:** the worker logs each decision as `forever route` with the sim id,
  the status, the refusal codes, the failing stage and the step timings.
- **Stored reports:** a routed sim's engine version is
  `forever-rust-<rust revision>-ref-<pin>`, so every sim a release served can be found
  later, and a stored report keeps the identity of the engine that made it.

A refusal measures coverage, and a fault is a failure. On a fault or a correctness report, roll
back as below, accept the request as a fixture with `python3 tools/prepared_v2.py accept`, and
fix it in a new release; never widen the gate to admit it.

## Roll back

Point `FOREVER_ROUTE_BUNDLE` at the previous release's bundle and restart the worker. Keep at
least the two most recent release bundles on the worker machine for this. Sims already served
keep their results and engine version.

Back up the worker's environment file before the change, change only the line named, and confirm
the worker's start log before calling the rollback done.
