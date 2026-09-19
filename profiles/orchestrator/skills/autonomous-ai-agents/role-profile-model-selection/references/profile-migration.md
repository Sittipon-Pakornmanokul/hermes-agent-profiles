# Profile-preserving interface migration

## Choose the smallest change
1. Establish whether the user wants a different interface, desktop removal, or a clean Agent installation. Removing Desktop does not require deleting Agent data. Prefer trying the official web dashboard before proposing a custom mission-control application.
2. Verify `hermes dashboard --help` in the installed version. The inspected CLI supported `hermes dashboard --host 127.0.0.1 --port 9119`; named-profile launches attached to one machine-level dashboard by default, while `--isolated` requested a separate server. Recheck current behavior rather than promising universal profile multiplexing.
3. Evaluate settings access, task delegation, independent review, cancellation and completion before accepting an alternative interface. Distinguish documented features, tested workflow and unimplemented lifecycle behavior. A localhost UI can still make outbound provider calls; preserve ZDR across main and auxiliary routes.

## Inventory without exposing secrets
1. List immediate file names, ownership and symlink targets under the resolved default home and every named-profile home. Do not print `.env`, authentication tokens or vault values. Inventory desktop app bundles and macOS application-support/cache/preferences separately.
2. Preserve the default profile's `config.yaml`, `.env`, `auth.json`, `SOUL.md`, `profile.yaml`, `memories/`, `skills/` and `.no-bundled-skills` when present. Preserve the same data under `profiles/<name>/`; top-level files alone do not restore specialist roles.
3. Preserve the complete local `vault/`, including its encryption key. Retain profile-specific `mcp-tokens/`, `secrets/` and `integrations/` when present; authentication may still need renewal after reinstall, so do not promise that copying tokens guarantees a login.
4. Offer continuity separately: session databases and `sessions/`; project/task/shared databases; workflows, hooks, plugins, pairing/platform state; user assets, artifacts, plans and workspaces. Identify actual files instead of treating every directory as a cache. Review restored schedules before allowing them to execute.

## Back up before clean installation
1. Consult `hermes backup --help` and inspect the current backup inclusion/exclusion rules. Prefer a full backup over `--quick` for migration. The inspected command supported `hermes -p default backup --keep 0`, retaining older backup archives and excluding the program checkout; verify profile coverage in the resulting archive rather than assuming it.
2. Store the archive outside the tree being removed, restrict access and treat it as containing secrets; do not assume a ZIP is encrypted. Verify archive integrity and named-profile entries before deleting anything. For external memory providers or symlinked data, verify what the backup actually captured.
3. Use SQLite-aware backup rather than copying a live database alone; uncheckpointed WAL changes can otherwise be lost. Do not restore stale WAL/SHM files alongside a fresh database snapshot.
4. Keep a recovery archive, then restore selectively into the clean installation. Restore personal configuration, instructions, memories and skills; review plugin, hook and scheduling settings before activation. Recheck all OpenRouter ZDR settings before model calls. A clean install does not automatically preserve a privacy policy.

## Remove only the obsolete surface
1. Establish an independent dashboard or CLI session before quitting/removing Desktop; the current assistant may depend on the desktop-owned backend. Never use a broad server-stop command without verifying it will preserve the user's dashboard and active work.
2. Remove verified desktop app bundles, desktop-only caches/preferences and generated build outputs, preferably via recoverable Trash. Explain that application-support data may contain uploads, browser state and saved connection details before removing it.
3. Preserve the Agent repository, runtime, dashboard build and shared dependencies for desktop-only removal. Keep tracked desktop source in an otherwise retained checkout; deleting it damages repository integrity without being necessary to remove the installed app.
4. For a true clean reinstall, replace the old program checkout rather than restoring local patches, virtual environments, dependency trees, generated builds, PID/lock files or transient process state. Keep user work products even when stored near caches.
5. Inventory task-created patches, reports and test environments separately. Revert only identified task-owned source changes, preserving unrelated user work; avoid blanket reset/clean. Exclude obsolete investigation artifacts from selective restoration while preserving reusable workflow procedures.
6. Verify the surviving dashboard/CLI and restored profile inventory before declaring removal or migration complete. Report backup created, archive verified, code installed, data restored and behavior tested as separate states. Do not claim a clean migration from a file list alone.
