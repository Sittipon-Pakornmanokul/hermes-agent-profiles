# Changelog

## Unreleased

- Shortened repeated profile instructions and made direct execution the default for small clear tasks.
- Limited delegation/review to justified work while preserving required independent review and approvals.
- Reduced handoff paperwork and repeated verification; retained bounded process waits.
- Workflow refresh now applies the same instruction policy without changing model or reasoning settings.


## 0.1.0 â€” 2026-09-21

First numbered release of the existing portable profile bundle.

### Added

- Role-specific context and verification efficiency instructions for all seven profiles.
- Handoff fields for unfinished work, evidence freshness and check invalidation.
- `VERSION` as the bundle version source and `bundle_version` in the export manifest.

### Changed

- Start fresh workers after accepted milestones; preserve unresolved debugging context.
- Keep routine tool output concise, with full logs stored locally when appropriate.
- Reuse checks only while relevant inputs remain unchanged; retain required independent review, source verification, business read-back and UX checks.
- Extend the existing named workflow handoffs with evidence and continuation fields; preserve the current import/update and export behavior.
- Preserve LF line endings through Git so manifest checksums remain portable.
- Preserve model, reasoning and approval settings during these instruction updates.

### Included baseline

- Seven specialist profiles, direct folder import/export, portable workflow defaults and an optional search-pattern patch.
- Credentials, memory, sessions and task history excluded from the export.

### Validation and limits

- Fresh export, instruction idempotency and manifest integrity checked on Windows.
- Native macOS execution and measured token savings have not been verified.
