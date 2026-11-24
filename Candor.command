#!/bin/sh
# Candor on a Mac: double-click it in Finder, or run ./Candor.command in Terminal.
# The macOS counterpart of Candor.cmd. There is no installer: run
# `python3 harness_setup.py` once first so the prerequisites are in place.
cd "$(dirname "$0")" || exit 1

pause() {
    # A double-click closes the Terminal window when this exits, taking the message with
    # it. Only wait when someone is there to read it.
    [ -t 0 ] && { printf '\nPress Return to close this window. '; read -r _; }
}

if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
else
    PY=""
    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1; then PY="$candidate"; break; fi
    done
fi

if [ -z "$PY" ]; then
    echo "Candor needs Python 3.10 or newer."
    echo "Install it from https://www.python.org/downloads/ and run this again."
    pause
    exit 1
fi

if ! "$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "Candor needs Python 3.10 or newer; $PY is $("$PY" -V 2>&1)."
    echo "Install a newer Python from https://www.python.org/downloads/ and run this again."
    pause
    exit 1
fi

if ! "$PY" -c 'import yaml, openpyxl, pypdf' 2>/dev/null; then
    echo "Candor's Python packages are missing. Run this once in Terminal, then try again:"
    echo
    echo "    uv sync"
    pause
    exit 1
fi

exec "$PY" -m app.launcher
