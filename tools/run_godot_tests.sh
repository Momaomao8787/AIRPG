#!/usr/bin/env bash
set -euo pipefail

GODOT_BIN="${GODOT_BIN:?GODOT_BIN must be set to the Godot executable path}"
PROJECT_DIR="${1:-client}"

if [[ ! -f "$PROJECT_DIR/project.godot" ]]; then
  echo "No Godot project at $PROJECT_DIR/project.godot"
  exit 1
fi

GODOT_OUTPUT_ERROR_PATTERN='SCRIPT ERROR|Parse Error|Failed to load script|Failed loading resource'

has_output_errors() {
  local log_file="$1"
  if grep -qE "$GODOT_OUTPUT_ERROR_PATTERN" "$log_file"; then
    return 0
  fi
  return 1
}

run_and_check() {
  local label="$1"
  shift
  local log_file
  log_file="$(mktemp)"
  echo "=== $label ==="
  set +e
  "$GODOT_BIN" --headless --path "$PROJECT_DIR" "$@" 2>&1 | tee "$log_file"
  local exit_code="${PIPESTATUS[0]}"
  set -e
  if has_output_errors "$log_file"; then
    echo "FAIL: $label — output contains SCRIPT ERROR, Parse Error, Failed to load script, or Failed loading resource"
    rm -f "$log_file"
    return 1
  fi
  if [[ "$exit_code" -ne 0 ]]; then
    echo "FAIL: $label — exit code $exit_code"
    rm -f "$log_file"
    return "$exit_code"
  fi
  echo "PASS: $label"
  rm -f "$log_file"
  return 0
}

overall=0

echo "=== Godot import ==="
if ! run_and_check "import" --import; then
  overall=1
fi

mapfile -t test_scripts < <(find "$PROJECT_DIR" -path '*/.godot/*' -prune -o -name '*_test.gd' -type f -print | sort)
if [[ ${#test_scripts[@]} -eq 0 ]]; then
  echo "No *_test.gd scripts found under $PROJECT_DIR"
else
  for script_path in "${test_scripts[@]}"; do
    rel="${script_path#"$PROJECT_DIR"/}"
    res_path="res://${rel}"
    if ! run_and_check "script $res_path" -s "$res_path"; then
      overall=1
    fi
  done
fi

main_scene=""
while IFS= read -r line; do
  if [[ "$line" =~ ^run/main_scene=\"(.+)\"$ ]]; then
    main_scene="${BASH_REMATCH[1]}"
    break
  fi
done < "$PROJECT_DIR/project.godot"

if [[ -z "$main_scene" ]]; then
  echo "WARN: run/main_scene not set in project.godot; skipping main scene run"
else
  if ! run_and_check "main scene $main_scene (quit-after 300)" --quit-after 300; then
    overall=1
  fi
fi

exit "$overall"
