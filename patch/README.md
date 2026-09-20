# Hermes search patch

## Summary

Preserves regex/glob backslashes when Hermes searches through ripgrep or grep. The original bug is Windows-specific. Windows search tests pass; native macOS execution has not been tested. Profile import works independently of this optional patch.

## Check and apply

Use the Python interpreter from your Hermes installation. Replace the paths below with your installation's paths and run from this patch folder:

```text
python apply_patch.py --repo /absolute/path/to/hermes-agent --check
python apply_patch.py --repo /absolute/path/to/hermes-agent
python verify_search.py --repo /absolute/path/to/hermes-agent
```

The installer checks the source version, refuses incompatible/local changes and saves a timestamped backup beside the modified file. Already-patched files are left unchanged. The verification script requires Hermes dependencies, bash, ripgrep and grep; it uses temporary files and makes no model/API calls.

On macOS, first run the verification script to establish whether a patch is needed. A common source location is `$HOME/.hermes/hermes-agent`; confirm your actual location. Do not bypass a version-mismatch rejection.

Restart the Hermes backend and workers at a safe stopping point to load the fix. The scripts never stop agents automatically. A Hermes update may replace or supersede this patch.

## Restore

Stop the affected backend and copy the generated `file_operations_search.py.backup-*` over `tools/file_operations_search.py`, provided no later update or edit has changed that file. Restart Hermes and rerun the verification script.

## Verified updated source

Adapted on September 21, 2026 (Asia/Bangkok) to Hermes commit `2ed6387d87`.
The original nine failing Windows search checks now pass, along with escaped
content/filename glob checks for both ripgrep and the grep/find fallback.
The fix keeps regex/glob data separate from filesystem-path normalization and
preserves backslashes through Git Bash. Only `tools/file_operations_search.py`
is changed in the installed Hermes checkout.

The installer remains exact-source-hash gated. Dry-run, exact backup, Windows
line-ending preservation, repeated application, and rejection of locally changed
source were verified in a temporary checkout. Older or newer unmatched versions
are refused; do not force this patch across updates.

Hermes' canonical test runner was attempted for the six focused search test files,
but could not start because the installed Python environment lacks pytest. The
standalone real-tool regression suite passed on Windows; native macOS testing
remains outstanding. No model/API requests were made.

For pre-installation verification of a reviewed candidate module:

```text
python verify_search.py --repo /path/to/hermes-agent --candidate /path/to/file_operations_search.py
```
