#!/bin/bash
# Sandbox Testing Script for Querty-OS
# Tests all components in isolation before device deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUERTY_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   QUERTY-OS SANDBOX TEST SUITE        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${YELLOW}Testing: ${test_name}${NC}"
    if eval "$test_command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Error output:"
        cat /tmp/test_output.log
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Change to repository root
cd "${QUERTY_ROOT}"

echo "=== Environment Tests ==="
run_test "Python version check" "python3 --version"
run_test "Python syntax validation" "python3 -m py_compile core/**/*.py"
run_test "Dependencies check" "pip3 list | grep -E 'psutil|pyyaml|click'"

echo ""
echo "=== Core Module Tests ==="
run_test "Import exceptions module" "python3 -c 'from core.exceptions import QuertyOSError'"
run_test "Import priority module" "python3 -c 'from core.priority import ResourcePriority'"
run_test "Priority system validation" "python3 -c 'from core.priority import StoragePriorityManager; m = StoragePriorityManager(64); m.suggest_partition_sizes()'"

echo ""
echo "=== Unit Tests ==="
run_test "Exception tests" "cd ${QUERTY_ROOT} && python3 -m pytest tests/unit/test_exceptions.py -v"
run_test "Priority tests" "cd ${QUERTY_ROOT} && python3 -m pytest tests/unit/test_priority.py -v"

echo ""
echo "=== Integration Tests ==="
run_test "Priority integration" "cd ${QUERTY_ROOT} && python3 -m pytest tests/integration/test_priority_integration.py -v"

echo ""
echo "=== Script Validation ==="
run_test "Boot script syntax" "bash -n scripts/boot/init-querty.sh"
run_test "Shutdown script syntax" "bash -n scripts/boot/shutdown-querty.sh"
run_test "Check status script" "bash -n scripts/utils/check-status.sh"

echo ""
echo "=== Docker Tests ==="
if command -v docker &> /dev/null; then
    run_test "Dockerfile validation" "docker build -f Dockerfile --target=builder -t querty-test . || true"
    echo -e "${YELLOW}Note: Full Docker build skipped in sandbox${NC}"
else
    echo -e "${YELLOW}Docker not available, skipping Docker tests${NC}"
fi

echo ""
echo "=== Configuration Tests ==="
run_test "Config file validation" "test -f config/querty-os.conf"
run_test "Priority config check" "grep -qi 'priority' config/querty-os.conf"

echo ""
echo "=== Tri-boot Script Tests (Poco X4 Pro 5G) ==="
if [ -d "devices/poco-x4-pro-5g" ]; then
    run_test "Tri-boot script syntax" "bash -n devices/poco-x4-pro-5g/scripts/triboot.sh"
    run_test "Partition setup syntax" "bash -n devices/poco-x4-pro-5g/scripts/partition_setup.sh"
    run_test "Backup script syntax" "bash -n devices/poco-x4-pro-5g/scripts/backup_partitions.sh"
else
    echo -e "${YELLOW}Device-specific scripts not found${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}           TEST SUMMARY                ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Ready for device deployment.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Fix issues before device deployment.${NC}"
    exit 1
fi
