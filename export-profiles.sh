#!/usr/bin/env bash
# macOS / POSIX launcher; does not activate or change the caller's environment.
set -euo pipefail
bundle_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source_dir="${HERMES_HOME:-${HOME}/.hermes}"
if [[ "$source_dir" == '~/'* ]]; then source_dir="${HOME}/${source_dir:2}"; fi
source_dir="${source_dir%/}"
if [[ "$(basename -- "$(dirname -- "$source_dir")")" == profiles ]]; then
  source_dir="$(dirname -- "$(dirname -- "$source_dir")")"
fi
output_dir="${PWD}"
repo_dir=""
python_bin=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --source|--dest|--repo|--python)
      if [ "$#" -lt 2 ]; then printf 'Missing value for %s\n' "$1" >&2; exit 2; fi
      case "$1" in
        --source) source_dir="$2" ;;
        --dest) output_dir="$2" ;;
        --repo) repo_dir="$2" ;;
        --python) python_bin="$2" ;;
      esac
      shift 2 ;;
    --help|-h)
      printf '%s\n' 'Usage: bash export-profiles.sh [--source HERMES_HOME] [--repo HERMES_REPO] [--python HERMES_PYTHON_PATH] [--dest FOLDER]' 'Export defaults to the current working directory.'
      exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
if [ -z "$repo_dir" ]; then repo_dir="$source_dir/hermes-agent"; fi
if [ -z "$python_bin" ]; then
  for candidate in "$repo_dir/.venv/bin/python" "$repo_dir/venv/bin/python"; do
    if [ -x "$candidate" ]; then python_bin="$candidate"; break; fi
  done
fi
if [ -z "$python_bin" ] || [ ! -x "$python_bin" ]; then
  printf '%s\n' 'Pass --python with the full path to the Hermes Python interpreter.' >&2
  exit 2
fi
exec "$python_bin" "$bundle_dir/export_profiles.py" --source "$source_dir" --repo "$repo_dir" --dest "$output_dir"
