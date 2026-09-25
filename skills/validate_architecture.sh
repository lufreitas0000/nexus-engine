#!/bin/sh
# Usage: ./skills/validate_architecture.sh [package_name]
set -eu

PKG="${1:-}"
TARGET_DIR="packages/${PKG}"

if [ -n "$PKG" ] && [ ! -d "$TARGET_DIR" ]; then
    echo "[FAIL] Package directory $TARGET_DIR does not exist."
    exit 1
fi

check_pkg() {
    pkg_path="$1"
    pkg_name=$(basename "$pkg_path")
    src_root="${pkg_path}/src/${pkg_name}"

    echo "=== Validating PEP 517 Layout: ${pkg_name} ==="
    if [ ! -d "$src_root" ]; then
        echo "[FAIL] Missing PEP 517 namespace directory: ${src_root}"
        return 1
    fi

    if [ -d "${pkg_path}/test" ]; then
        echo "[FAIL] Legacy 'test/' directory still exists in ${pkg_path}. Merge into 'tests/'."
        return 1
    fi

    # Check for forbidden I/O imports inside domain/
    if [ -d "${src_root}/domain" ]; then
        if grep -RInE "^[[:space:]]*(import|from)[[:space:]]+(sqlite3|aiosqlite|httpx|requests|subprocess|shutil|fastapi|webview|typer|nexus_db)" "${src_root}/domain" 2>/dev/null; then
            echo "[FAIL] Impure I/O or framework import detected in ${src_root}/domain"
            return 1
        fi
    fi
    echo "[OK] ${pkg_name} layout and domain purity verified."
}

if [ -n "$PKG" ]; then
    check_pkg "$TARGET_DIR"
else
    for d in packages/*/; do
        check_pkg "${d%/}"
    done
fi
