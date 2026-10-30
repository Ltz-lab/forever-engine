# Working in this repository

- New Forever work happens here only: do not patch the Go fork or port upstream wowsims commits.
- Keep every accepted Go golden passing. Do not rewrite goldens just to agree with a changed
  implementation.
- Check Rust-only mechanics against the client rows and tooltips (README, Rust-only mechanics).
- Keep class spells and talents in their class domain, spec behavior in that class's specs
  domain, and reusable primitives in core/mechanics. Shared code must not import classes.
- Do not use em dashes or en dashes in prose, comments, commits or Markdown.
- Use the configured human Git author. No AI coauthor trailers, generation footers, task links
  or session links in commits and PRs.
- Name a branch after the change itself, such as `feral-bear-parity`, never with a `claude/`
  prefix or any other tool or agent prefix.
