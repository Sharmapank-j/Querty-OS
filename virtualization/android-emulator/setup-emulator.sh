#!/bin/bash
# Android Emulator Setup for Querty-OS Testing
# Sets up Android Virtual Device (AVD) for testing Querty-OS on Android

set -e

# Configuration
AVD_NAME="Querty_OS_Test"
DEVICE_TYPE="pixel_6"
API_LEVEL="33"  # Android 13
ABI="x86_64"    # or "arm64-v8a" for ARM
IMAGE_TAG="google_apis"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Querty-OS Android Emulator Setup${NC}"
echo "====================================="

# Check if Android SDK is installed
if [ -z "$ANDROID_HOME" ]; then
    echo -e "${RED}Error: ANDROID_HOME not set${NC}"
    echo "Install Android SDK and set ANDROID_HOME environment variable"
    echo "Example: export ANDROID_HOME=\$HOME/Android/Sdk"
    exit 1
fi

SDKMANAGER="${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager"
AVDMANAGER="${ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager"
EMULATOR="${ANDROID_HOME}/emulator/emulator"

# Check if tools exist
if [ ! -f "$SDKMANAGER" ]; then
    echo -e "${RED}Error: sdkmanager not found${NC}"
    echo "Install Android command-line tools"
    exit 1
fi

# Install required system images
echo "Installing Android system image..."
${SDKMANAGER} "system-images;android-${API_LEVEL};${IMAGE_TAG};${ABI}"
${SDKMANAGER} "platforms;android-${API_LEVEL}"
${SDKMANAGER} "platform-tools"
${SDKMANAGER} "emulator"

# Create AVD
echo "Creating Android Virtual Device..."
echo "no" | ${AVDMANAGER} create avd \
    -n "${AVD_NAME}" \
    -k "system-images;android-${API_LEVEL};${IMAGE_TAG};${ABI}" \
    -d "${DEVICE_TYPE}" \
    --force

# Configure AVD
AVD_CONFIG="${HOME}/.android/avd/${AVD_NAME}.avd/config.ini"
if [ -f "$AVD_CONFIG" ]; then
    echo "Configuring AVD settings..."
    # Increase RAM and storage for Querty-OS
    sed -i 's/^hw.ramSize=.*/hw.ramSize=8192/' "$AVD_CONFIG"
    sed -i 's/^disk.dataPartition.size=.*/disk.dataPartition.size=8G/' "$AVD_CONFIG"
    sed -i 's/^hw.keyboard=.*/hw.keyboard=yes/' "$AVD_CONFIG"
    
    # Add lines if they don't exist
    grep -q "^hw.cpu.ncore=" "$AVD_CONFIG" || echo "hw.cpu.ncore=4" >> "$AVD_CONFIG"
    grep -q "^hw.gpu.enabled=" "$AVD_CONFIG" || echo "hw.gpu.enabled=yes" >> "$AVD_CONFIG"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "AVD created: ${AVD_NAME}"
