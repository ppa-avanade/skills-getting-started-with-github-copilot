#!/bin/bash

# Test runner script for High School Management System API
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Change to project directory
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Using virtual environment${NC}"
    PYTHON_CMD=".venv/bin/python"
else
    echo -e "${YELLOW}Using system python${NC}"
    PYTHON_CMD="python"
fi

echo -e "${GREEN}Running FastAPI tests...${NC}"

# Default arguments
PYTEST_ARGS="-v"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            PYTEST_ARGS="$PYTEST_ARGS --cov=src --cov-report=html --cov-report=term"
            echo -e "${YELLOW}Coverage reporting enabled${NC}"
            shift
            ;;
        --fast)
            PYTEST_ARGS="$PYTEST_ARGS -x"
            echo -e "${YELLOW}Fast mode: stopping on first failure${NC}"
            shift
            ;;
        --verbose)
            PYTEST_ARGS="$PYTEST_ARGS -vv"
            echo -e "${YELLOW}Extra verbose mode enabled${NC}"
            shift
            ;;
        --quiet)
            PYTEST_ARGS="-q"
            echo -e "${YELLOW}Quiet mode enabled${NC}"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --coverage    Generate coverage report"
            echo "  --fast        Stop on first failure"
            echo "  --verbose     Extra verbose output"
            echo "  --quiet       Minimal output"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! $PYTHON_CMD -c "import pytest" 2>/dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Please install requirements: $PYTHON_CMD -m pip install -r requirements.txt"
    exit 1
fi

# Check if httpx is installed (required for FastAPI testing)
if ! $PYTHON_CMD -c "import httpx" 2>/dev/null; then
    echo -e "${RED}Error: httpx is not installed${NC}"
    echo "Please install requirements: $PYTHON_CMD -m pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}Starting test execution...${NC}"
echo "Command: $PYTHON_CMD -m pytest tests/ $PYTEST_ARGS"
echo ""

# Run the tests
if $PYTHON_CMD -m pytest tests/ $PYTEST_ARGS; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    
    # If coverage was requested, show where the report is
    if [[ $PYTEST_ARGS == *"--cov"* ]]; then
        echo -e "${YELLOW}📊 Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi