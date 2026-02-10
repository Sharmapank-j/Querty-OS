#!/bin/bash
# QEMU/KVM Setup Script for Querty-OS
# This script creates and configures a QEMU virtual machine for testing Querty-OS

set -e

# Configuration
VM_NAME="querty-os-vm"
VM_DISK_SIZE="64G"
VM_MEMORY="8192"  # 8GB
VM_CPUS="4"
VM_DISK_IMAGE="${VM_NAME}.qcow2"
ISO_PATH="${ISO_PATH:-ubuntu-22.04-server-arm64.iso}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Querty-OS QEMU/KVM Setup${NC}"
echo "=================================="

# Check if QEMU is installed
if ! command -v qemu-system-aarch64 &> /dev/null && ! command -v qemu-system-x86_64 &> /dev/null; then
    echo -e "${RED}Error: QEMU not found${NC}"
    echo "Install with: sudo apt-get install qemu-system qemu-kvm"
    exit 1
fi

# Check if KVM is available
if [ ! -e /dev/kvm ]; then
    echo -e "${YELLOW}Warning: KVM not available, will use software emulation (slower)${NC}"
    KVM_OPTS=""
else
    echo -e "${GREEN}KVM acceleration available${NC}"
    KVM_OPTS="-enable-kvm"
fi

# Create disk image if it doesn't exist
if [ ! -f "${VM_DISK_IMAGE}" ]; then
    echo "Creating virtual disk image (${VM_DISK_SIZE})..."
    qemu-img create -f qcow2 "${VM_DISK_IMAGE}" "${VM_DISK_SIZE}"
else
    echo -e "${YELLOW}Disk image already exists: ${VM_DISK_IMAGE}${NC}"
fi

# Create VM configuration file
cat > qemu-config.txt <<EOF
# Querty-OS QEMU Configuration
VM_NAME=${VM_NAME}
VM_DISK_IMAGE=${VM_DISK_IMAGE}
VM_MEMORY=${VM_MEMORY}
VM_CPUS=${VM_CPUS}
VM_NETWORK=user,hostfwd=tcp::8080-:8080,hostfwd=tcp::8081-:8081,hostfwd=tcp::2222-:22
EOF

echo "Configuration saved to qemu-config.txt"

# Create start script
cat > start-vm.sh <<'EOF'
#!/bin/bash
# Start Querty-OS VM

source qemu-config.txt

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
    QEMU_CMD="qemu-system-aarch64"
    MACHINE_TYPE="-M virt"
    CPU_TYPE="-cpu cortex-a72"
else
    QEMU_CMD="qemu-system-x86_64"
    MACHINE_TYPE="-M q35"
    CPU_TYPE="-cpu host"
fi

echo "Starting ${VM_NAME}..."
echo "Connect via SSH: ssh -p 2222 querty@localhost"
echo "API: http://localhost:8080"
echo "Monitor: http://localhost:8081"

${QEMU_CMD} \
    ${MACHINE_TYPE} \
    ${CPU_TYPE} \
    -m ${VM_MEMORY} \
    -smp ${VM_CPUS} \
    -drive file=${VM_DISK_IMAGE},format=qcow2,if=virtio \
    -net nic,model=virtio \
    -net ${VM_NETWORK} \
    -nographic \
    -serial mon:stdio \
    ${KVM_OPTS:-}
EOF

chmod +x start-vm.sh

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run: ./start-vm.sh"
echo "2. Install Ubuntu in the VM"
echo "3. SSH into VM: ssh -p 2222 querty@localhost"
echo "4. Clone and setup Querty-OS in the VM"
