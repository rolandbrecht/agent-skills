#!/usr/bin/env bash
# Install ast-grep. Tries each available package manager in order and
# continues with the next one when an attempt fails.
# Usage: bash install.sh
set -u

if command -v ast-grep >/dev/null 2>&1; then
  echo "ast-grep is already installed: $(ast-grep --version)"
  exit 0
fi

echo "ast-grep not found. Trying available package managers..."

try_install() {
  local manager="$1"; shift
  command -v "$manager" >/dev/null 2>&1 || return 1
  echo "Attempting install via $manager..."
  if "$@"; then
    if command -v ast-grep >/dev/null 2>&1; then
      return 0
    fi
    echo "$manager reported success, but ast-grep is not on PATH. Trying next manager..."
    return 1
  fi
  echo "Install via $manager failed. Trying next manager..."
  return 1
}

installed=false
try_install brew brew install ast-grep && installed=true
$installed || { try_install cargo cargo install ast-grep --locked && installed=true; }
$installed || { try_install npm npm install -g @ast-grep/cli && installed=true; }
# --user avoids PEP 668 "externally managed environment" failures on system Python
$installed || { try_install pip3 pip3 install --user ast-grep-cli && installed=true; }
if ! $installed && command -v port >/dev/null 2>&1; then
  if [ -t 0 ]; then
    try_install port sudo port install ast-grep && installed=true
  else
    echo "Skipping MacPorts: 'sudo port' needs an interactive terminal."
  fi
fi

if ! $installed; then
  echo "ERROR: could not install ast-grep (tried brew, cargo, npm, pip3, port)." >&2
  echo "See https://ast-grep.github.io/guide/quick-start.html for manual installation." >&2
  exit 1
fi

echo "Verification:"
ast-grep --version
