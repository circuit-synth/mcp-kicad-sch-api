# Run Integration Tests

Runs comprehensive integration tests for the MCP KiCAD Schematic API server with real KiCAD files.

## Command

```bash
pytest tests/test_mcp_server_integration.py -v
```

## What this does

- Tests complete MCP tool workflows
- Creates, modifies, and saves real KiCAD schematic files
- Validates component addition with properties
- Tests wire connections and labels
- Verifies round-trip file operations
- Checks all MCP tools work with actual KiCAD API

## Test categories

1. **Schematic Operations**: create, load, save workflows
2. **Component Management**: add components with footprints and properties  
3. **Wire Connections**: add wires between specific points
4. **Label Functionality**: local and hierarchical labels
5. **Junction Support**: connection points for wires
6. **File Operations**: save/load with format preservation

## Expected output

- All integration tests pass
- Temporary KiCAD files created and cleaned up
- Real KiCAD API calls succeed
- MCP tools produce valid schematic elements

## When to use

- Before releasing new versions
- After modifying MCP tool implementations
- When adding new KiCAD functionality
- To verify real-world usage scenarios