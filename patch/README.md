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
