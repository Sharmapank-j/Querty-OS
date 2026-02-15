#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DEVICE_CODE=""
SKIP_PUSH=0

usage() {
  cat <<EOF
Usage: $0 [--device veux|peux] [--skip-push]

Host-side verification + deployment helper for a fresh MIUI/HyperOS install.
- Verifies repository integrity and required files
- Verifies adb/fastboot + connected Poco X4 Pro 5G
- Optionally pushes Querty-OS sources to /sdcard/Querty-OS
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --device) DEVICE_CODE="$2"; shift 2 ;;
    --skip-push) SKIP_PUSH=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "[ERROR] Missing required command: $1"; exit 1; }
}

assert_file() {
  [[ -f "$1" ]] || { echo "[ERROR] Missing required file: $1"; exit 1; }
}

echo "[INFO] Validating local repository files..."
assert_file "$REPO_ROOT/README.md"
assert_file "$REPO_ROOT/requirements.txt"
assert_file "$REPO_ROOT/devices/poco-x4-pro-5g/scripts/partition_setup.sh"
assert_file "$REPO_ROOT/devices/poco-x4-pro-5g/scripts/triboot.sh"
assert_file "$REPO_ROOT/systemd/querty-ai-daemon.service"

for sh_file in \
  "$REPO_ROOT/devices/poco-x4-pro-5g/scripts/partition_setup.sh" \
  "$REPO_ROOT/devices/poco-x4-pro-5g/scripts/triboot.sh" \
  "$REPO_ROOT/devices/poco-x4-pro-5g/scripts/fresh_mirom_setup.sh"
do
  bash -n "$sh_file"
done

require_cmd adb
require_cmd fastboot
require_cmd python3

echo "[INFO] Checking connected Android device..."
adb start-server >/dev/null
ADB_STATE="$(adb get-state 2>/dev/null || true)"
if [[ "$ADB_STATE" != "device" ]]; then
  echo "[ERROR] No authorized adb device detected. Enable USB debugging and authorize this computer."
  exit 1
fi

CONNECTED_CODE="$(adb shell getprop ro.product.device 2>/dev/null | tr -d '\r')"
if [[ -n "$DEVICE_CODE" && "$CONNECTED_CODE" != "$DEVICE_CODE" ]]; then
  echo "[ERROR] Device mismatch. Expected '$DEVICE_CODE', got '$CONNECTED_CODE'."
  exit 1
fi

if [[ "$CONNECTED_CODE" != "veux" && "$CONNECTED_CODE" != "peux" ]]; then
  echo "[ERROR] Unsupported device '$CONNECTED_CODE'. This script supports Poco X4 Pro 5G (veux/peux)."
  exit 1
fi

MIUI_VERSION="$(adb shell getprop ro.miui.ui.version.name 2>/dev/null | tr -d '\r')"
ANDROID_VERSION="$(adb shell getprop ro.build.version.release 2>/dev/null | tr -d '\r')"
UNLOCK_STATE="$(adb shell getprop ro.boot.flash.locked 2>/dev/null | tr -d '\r')"

echo "[INFO] Device codename: $CONNECTED_CODE"
echo "[INFO] MIUI/HyperOS version: ${MIUI_VERSION:-unknown}"
echo "[INFO] Android version: ${ANDROID_VERSION:-unknown}"
if [[ "$UNLOCK_STATE" == "1" ]]; then
  echo "[WARN] Bootloader appears locked. Unlock before Querty-OS boot setup steps."
fi

if [[ "$SKIP_PUSH" -eq 0 ]]; then
  echo "[INFO] Deploying sources to phone: /sdcard/Querty-OS"
  adb shell "mkdir -p /sdcard/Querty-OS"
  adb push "$REPO_ROOT" "/sdcard/Querty-OS" >/dev/null
  echo "[INFO] Deployment complete."
else
  echo "[INFO] --skip-push set; skipping source deployment."
fi

echo "[INFO] Fresh MIUI verification complete. Continue with POCO_X4_PRO_DEPLOYMENT.md phases 3-8."
