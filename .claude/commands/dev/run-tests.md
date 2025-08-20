# Test Runner Command - MCP KiCAD Schematic API

## Usage
```bash
/run-tests [options]
```

## Description
Orchestrates comprehensive testing for the MCP KiCAD Schematic API server, covering all MCP tools and KiCAD integration with professional test reporting.

## Options
- `--suite=standard` - Test suite: `quick`, `standard`, `integration`, `coverage` (default: standard)
- `--skip-install` - Skip dependency reinstallation (faster for development)
- `--keep-outputs` - Don't delete generated test files
- `--verbose` - Show detailed output
- `--fail-fast=false` - Stop on first failure (default: false)

## Test Suites

### 🚀 Quick Suite (~5 seconds)
Fast development testing:
```bash
pytest tests/test_server.py -q
```

### 📋 Standard Suite - Default (~15 seconds)
Comprehensive MCP server functionality:
```bash
# Run all tests
pytest tests/ -v --tb=short
```

### 🔬 Integration Suite (~30 seconds)
Complete validation with real KiCAD files:
```bash
# Integration tests with kicad-sch-api
pytest tests/test_mcp_server_integration.py -v

# Test MCP tool workflows
pytest tests/ -v -k "integration"
```

### 📊 Coverage Suite (~20 seconds)
Detailed coverage analysis:
```bash
pytest tests/ --cov=mcp_kicad_sch_api --cov-report=term-missing --cov-report=html --cov-fail-under=80
```

## Implementation

```bash
#!/bin/bash

# Parse arguments
SUITE="standard"
SKIP_INSTALL=false
KEEP_OUTPUTS=false
VERBOSE=false
FAIL_FAST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --suite=*)
            SUITE="${1#*=}"
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure we're in project root
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Must run from mcp-kicad-sch-api root"
    exit 1
fi

# Install dependencies if needed
if [[ "$SKIP_INSTALL" == "false" ]]; then
    echo "📦 Installing dependencies..."
    pip install -e . --quiet
    pip install -e submodules/kicad-sch-api --quiet
    pip install pytest pytest-cov --quiet
fi

# Build pytest arguments
PYTEST_ARGS=""
[[ "$VERBOSE" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -v"
[[ "$FAIL_FAST" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -x"

# Execute test suite
case $SUITE in
    quick)
        echo "🚀 Running quick test suite..."
        pytest tests/test_server.py -q $PYTEST_ARGS
        ;;
        
    standard)
        echo "📋 Running standard test suite..."
        pytest tests/ --tb=short $PYTEST_ARGS
        ;;
        
    integration)
        echo "🔬 Running integration test suite..."
        
        # MCP server integration tests
        pytest tests/test_mcp_server_integration.py -v $PYTEST_ARGS || exit 1
        
        # All integration workflows
        pytest tests/ -v -k "integration" $PYTEST_ARGS
        ;;
        
    coverage)
        echo "📊 Running coverage analysis..."
        pytest tests/ --cov=mcp_kicad_sch_api --cov-report=term-missing --cov-report=html --cov-fail-under=70 $PYTEST_ARGS
        echo "📊 Coverage report: htmlcov/index.html"
        ;;
        
    *)
        echo "❌ Unknown suite: $SUITE"
        echo "Available suites: quick, standard, integration, coverage"
        exit 1
        ;;
esac

# Cleanup if requested
if [[ "$KEEP_OUTPUTS" == "false" ]]; then
    echo "🧹 Cleaning up test outputs..."
    rm -rf .pytest_cache/ .coverage htmlcov/ test_*.kicad_sch 2>/dev/null || true
fi

echo "✅ Test suite completed"
```

## Expected Results by Suite

**Quick Suite**:
- ~5 tests, basic server functionality only
- <5 seconds execution time
- Good for rapid development iteration

**Standard Suite**:
- ~15-20 tests covering all MCP tools
- ~15 seconds execution time
- Recommended for pre-commit validation

**Integration Suite**:
- All tests + real KiCAD file operations
- ~30 seconds execution time
- Recommended for pre-merge validation

**Coverage Suite**:
- Same as Standard but with detailed coverage analysis
- Target: >80% code coverage
- Generates HTML coverage report

## Usage Examples

```bash
# Quick development check
/run-tests --suite=quick

# Standard pre-commit validation (default)
/run-tests

# Full integration testing before merge
/run-tests --suite=integration --verbose

# Coverage analysis
/run-tests --suite=coverage

# Debug specific failures
/run-tests --suite=standard --verbose --fail-fast

# Fast iteration during debugging
/run-tests --suite=quick --skip-install
```

## MCP Server Specific Testing

### Core MCP Tool Tests
- Tool registration and schemas
- Parameter validation
- Error handling
- Response formatting

### KiCAD Integration Tests
- Component addition workflows
- Wire connection functionality
- Label creation (local and hierarchical)
- Junction support
- Save/load operations

### Real-world Testing
- Create complete circuits
- Round-trip file operations
- Format preservation
- Performance with complex schematics

This command provides comprehensive testing for the MCP KiCAD Schematic API server while maintaining fast development iteration cycles.