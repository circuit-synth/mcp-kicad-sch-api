# Publish to PyPI - MCP KiCAD Schematic API

## Usage
```bash
/publish-pypi [options]
```

## Description
Builds and publishes the MCP KiCAD Schematic API server package to PyPI, making it available for installation via `pip install mcp-kicad-sch-api`.

## Options
- `--version=auto` - Version increment: `auto`, `patch`, `minor`, `major`, or specific version (e.g., `1.2.3`)
- `--test-pypi` - Upload to Test PyPI instead of production
- `--dry-run` - Build package but don't upload
- `--skip-tests` - Skip running tests before publishing
- `--force` - Bypass confirmation prompts

## Implementation

```bash
#!/bin/bash

# Parse arguments
VERSION="auto"
TEST_PYPI=false
DRY_RUN=false
SKIP_TESTS=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --version=*)
            VERSION="${1#*=}"
            shift
            ;;
        --test-pypi)
            TEST_PYPI=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --force)
            FORCE=true
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

# Get current version
CURRENT_VERSION=$(grep 'version = ' pyproject.toml | sed 's/.*version = "\(.*\)".*/\1/')
echo "📋 Current version: $CURRENT_VERSION"

# Calculate new version
if [[ "$VERSION" == "auto" ]]; then
    # Auto-increment patch version
    IFS='.' read -ra ADDR <<< "$CURRENT_VERSION"
    MAJOR="${ADDR[0]}"
    MINOR="${ADDR[1]}"
    PATCH="${ADDR[2]}"
    NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
elif [[ "$VERSION" == "patch" ]]; then
    IFS='.' read -ra ADDR <<< "$CURRENT_VERSION"
    MAJOR="${ADDR[0]}"
    MINOR="${ADDR[1]}"
    PATCH="${ADDR[2]}"
    NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
elif [[ "$VERSION" == "minor" ]]; then
    IFS='.' read -ra ADDR <<< "$CURRENT_VERSION"
    MAJOR="${ADDR[0]}"
    MINOR="${ADDR[1]}"
    NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
elif [[ "$VERSION" == "major" ]]; then
    IFS='.' read -ra ADDR <<< "$CURRENT_VERSION"
    MAJOR="${ADDR[0]}"
    NEW_VERSION="$((MAJOR + 1)).0.0"
else
    NEW_VERSION="$VERSION"
fi

echo "🚀 Publishing version: $NEW_VERSION"

# Confirmation
if [[ "$FORCE" == "false" ]]; then
    read -p "Continue with version $NEW_VERSION? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
fi

# Run tests first
if [[ "$SKIP_TESTS" == "false" ]]; then
    echo "🧪 Running tests..."
    pytest tests/ -v || { echo "❌ Tests failed"; exit 1; }
    echo "✅ Tests passed"
fi

# Update version in files
echo "📝 Updating version to $NEW_VERSION..."
sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/mcp_kicad_sch_api/__init__.py

# Clean up backup files
rm -f pyproject.toml.bak src/mcp_kicad_sch_api/__init__.py.bak

# Build package
echo "📦 Building package..."
python -m build || { echo "❌ Build failed"; exit 1; }

# Validate package
echo "✅ Validating package..."
python -m twine check dist/mcp_kicad_sch_api-$NEW_VERSION* || { echo "❌ Package validation failed"; exit 1; }

if [[ "$DRY_RUN" == "true" ]]; then
    echo "🏁 Dry run completed. Package built but not uploaded."
    echo "📦 Built: dist/mcp_kicad_sch_api-$NEW_VERSION*"
    exit 0
fi

# Upload to PyPI
if [[ "$TEST_PYPI" == "true" ]]; then
    echo "🚀 Uploading to Test PyPI..."
    python -m twine upload --repository testpypi dist/mcp_kicad_sch_api-$NEW_VERSION*
    echo "✅ Uploaded to Test PyPI: https://test.pypi.org/project/mcp-kicad-sch-api/$NEW_VERSION/"
else
    echo "🚀 Uploading to PyPI..."
    python -m twine upload dist/mcp_kicad_sch_api-$NEW_VERSION*
    echo "✅ Uploaded to PyPI: https://pypi.org/project/mcp-kicad-sch-api/$NEW_VERSION/"
fi

# Create git tag
echo "🏷️ Creating git tag..."
git add pyproject.toml src/mcp_kicad_sch_api/__init__.py
git commit -m "Release version $NEW_VERSION"
git tag "v$NEW_VERSION"
git push origin main --tags

echo "🎉 Release $NEW_VERSION completed successfully!"
echo "📦 Install with: pip install --upgrade mcp-kicad-sch-api"
```

## Prerequisites

- PyPI credentials configured (`~/.pypirc` or environment variables)
- Clean working directory
- All tests passing
- Proper version increment

## Usage Examples

```bash
# Auto-increment patch version and publish
/publish-pypi

# Publish specific version
/publish-pypi --version=1.0.0

# Increment minor version
/publish-pypi --version=minor

# Test upload to Test PyPI
/publish-pypi --test-pypi

# Build package without uploading
/publish-pypi --dry-run

# Quick publish without confirmation
/publish-pypi --force

# Publish without running tests (not recommended)
/publish-pypi --skip-tests
```

## What This Command Does

1. **Version Management**: Auto-increments version or uses specified version
2. **Testing**: Runs full test suite to ensure quality
3. **Building**: Creates wheel and source distributions
4. **Validation**: Checks package integrity with twine
5. **Upload**: Publishes to PyPI (or Test PyPI)
6. **Tagging**: Creates git tag and pushes to repository

## Expected Output

```
📋 Current version: 0.2.0
🚀 Publishing version: 0.2.1
🧪 Running tests...
✅ Tests passed
📝 Updating version to 0.2.1...
📦 Building package...
✅ Validating package...
🚀 Uploading to PyPI...
✅ Uploaded to PyPI: https://pypi.org/project/mcp-kicad-sch-api/0.2.1/
🏷️ Creating git tag...
🎉 Release 0.2.1 completed successfully!
```

## Post-Release Verification

```bash
# Test installation from PyPI
pip install --upgrade mcp-kicad-sch-api

# Verify MCP server works
python -m mcp_kicad_sch_api --version

# Test basic functionality
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | python -m mcp_kicad_sch_api
```

This command automates the entire release process for the MCP KiCAD Schematic API server.