# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL DEVELOPMENT RULES

### 🚫 Git Commit Policy
**NEVER commit changes unless explicitly told by the user.**
- Always ask for permission before running `git commit`
- Only commit when user specifically requests it
- Exception: Only commit automatically when user says "commit this" or similar explicit instruction

### 📦 Version Management Policy
**Always increment PyPI version by patch (0.0.1) unless instructed otherwise.**
- Default increment: `0.2.0` → `0.2.1` → `0.2.2`
- Only use minor/major increments when user explicitly requests
- Always update both `pyproject.toml` and `src/mcp_kicad_sch_api/__init__.py`

### 📋 Feature Development Policy
**Always create a PRD (Product Requirements Document) before implementing features.**
- Write a detailed PRD markdown file in the project root
- Include: Problem statement, proposed solution, technical approach, testing plan
- **ASK USER FOR FEEDBACK** on the PRD before proceeding with implementation
- Do not start coding until user approves the PRD

#### PRD Template:
```markdown
# PRD: [Feature Name]

## Problem Statement
[What problem are we solving?]

## Proposed Solution
[High-level approach]

## Technical Implementation
- [Technical details]
- [API changes]
- [Testing approach]

## Success Criteria
[How do we know it works?]
```

### 🔄 Required Workflow
1. **User requests feature** → Write PRD → **Ask for user approval**
2. **User approves PRD** → Implement feature → Run tests
3. **Implementation complete** → **Ask user if they want to commit**
4. **User says commit** → Commit with appropriate message
5. **User requests release** → Increment patch version → Publish to PyPI

## Project Overview

mcp-kicad-sch-api is a **Model Context Protocol (MCP) server** that provides KiCAD schematic manipulation tools for AI agents. It acts as a bridge between AI systems and KiCAD schematic files, enabling automated circuit design and analysis.

## Architecture

```
mcp-kicad-sch-api/
├── src/mcp_kicad_sch_api/           # MCP Server implementation
│   ├── __init__.py                  # Package initialization & CLI
│   ├── __main__.py                  # Entry point for server execution
│   └── server.py                    # Core MCP server with tool handlers
├── tests/                           # Comprehensive test suite
│   ├── test_server.py              # Basic server tests
│   └── test_mcp_server_integration.py # Integration tests with real KiCAD API
├── submodules/                      # Git submodules
│   └── kicad-sch-api/              # Core KiCAD manipulation library
├── pyproject.toml                   # Package configuration
└── README.md                        # User documentation
```

## Key Commands

### Development Environment Setup
```bash
# Install in development mode
pip install -e .

# Install with dependencies from submodule
pip install -e "submodules/kicad-sch-api"

# Install MCP SDK
pip install mcp
```

### Testing Commands
```bash
# Run all tests
pytest tests/ -v

# Run integration tests (requires kicad-sch-api)
pytest tests/test_mcp_server_integration.py -v

# Run specific test method
pytest tests/test_mcp_server_integration.py::TestMCPServerIntegration::test_add_component_workflow -v
```

### MCP Server Commands
```bash
# Run MCP server directly
python -m mcp_kicad_sch_api

# Run MCP server with verbose logging
python -m mcp_kicad_sch_api -vv

# Test server starts without errors
python -c "import sys; sys.path.insert(0, 'src'); from mcp_kicad_sch_api.server import main; print('✅ Server imports successfully')"
```

### Package Management
```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/mcp_kicad_sch_api-*

# Install latest from PyPI
pip install --upgrade mcp-kicad-sch-api
```

## Core MCP Server API

The server provides these MCP tools for AI agents:

```python
# Available MCP Tools:
- create_schematic(name: str) -> Creates new KiCAD schematic
- load_schematic(file_path: str) -> Loads existing schematic
- save_schematic(file_path?: str) -> Saves current schematic
- add_component(lib_id: str, reference: str, value: str, position: [x,y], footprint?: str) -> Adds component
- add_wire(start_pos: [x,y], end_pos: [x,y]) -> Connects two points
- add_label(text: str, position: [x,y], rotation?: float, size?: float) -> Adds text label
- add_hierarchical_label(text: str, position: [x,y], shape?: str) -> Adds interface label
- add_junction(position: [x,y], diameter?: float) -> Adds connection point
- search_components(query: str, library?: str, limit?: int) -> Searches component libraries
- list_components() -> Lists all components in schematic
- get_schematic_info() -> Gets schematic statistics and info
```

## Testing Strategy & MCP Integration

**CRITICAL**: This project depends on the `kicad-sch-api` library for actual KiCAD manipulation. Always verify MCP tool calls work correctly with real KiCAD files.

### MCP Server Testing
```bash
# Test MCP server functionality
pytest tests/test_mcp_server_integration.py -v

# Test specific workflows
pytest tests/test_mcp_server_integration.py::test_add_component_workflow -v
pytest tests/test_mcp_server_integration.py::test_add_wire_workflow -v
pytest tests/test_mcp_server_integration.py::test_save_and_load_workflow -v
```

### Manual MCP Testing
```bash
# Start MCP server and test tools manually
python -m mcp_kicad_sch_api

# Test with Claude Code or other MCP clients
# Use tools like: create_schematic, add_component, add_wire, etc.
```

## Key Principles

1. **MCP Protocol Compliance**: Follow MCP standards for tool definitions and responses
2. **KiCAD API Accuracy**: Use correct kicad-sch-api calls and parameters
3. **Error Handling**: Provide clear error messages for AI agents
4. **Tool Completeness**: Support all major KiCAD schematic elements
5. **Version Compatibility**: Maintain backward compatibility for MCP clients
6. **Professional Quality**: Comprehensive validation and testing

## Core Architecture Patterns

### MCP Server Implementation Notes
**This project uses the official MCP Python SDK 1.13.0 with low-level server API:**
- Uses `mcp.server.Server` (not FastMCP) for full control
- Single `@server.call_tool()` handler dispatches to individual tool logic
- Tools defined via `@server.list_tools()` with JSON schemas
- Our approach gives maximum control over MCP protocol implementation

**Alternative**: FastMCP provides simpler `@mcp.tool()` decorators but we chose the low-level approach for flexibility.

### MCP Tool Pattern
```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Single handler dispatches to individual tool logic based on name."""
    if name == "create_schematic":
        schematic_name = arguments.get("name", "untitled")
        current_schematic = ksa.create_schematic(schematic_name)
        return [TextContent(type="text", text=f"✅ Created: {schematic_name}")]
    # ... other tools
```

### Error Handling Pattern
```python
try:
    # KiCAD API call
    result = current_schematic.add_component(...)
    return [TextContent(type="text", text=f"✅ Success: {result}")]
except Exception as e:
    logger.error(f"Error in {name}: {e}")
    return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
```

### Parameter Validation Pattern
```python
if not all([lib_id, reference, value, position]):
    return [TextContent(type="text", text="❌ Required parameters missing")]

if len(position) != 2:
    return [TextContent(type="text", text="❌ Position must be [x, y] coordinates")]
```

## Claude Code Configuration

This project includes a `.claude/settings.json` file that configures Claude Code:

- **Default Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Commands Available**: 
  - Run tests, build package, update PyPI
  - Review implementation, analyze code
  - Update memory bank and documentation

## Dependencies

### Core Dependencies
- **mcp**: Model Context Protocol SDK for server implementation
- **kicad-sch-api**: KiCAD schematic manipulation (via submodule)
- **click**: CLI interface for server startup
- **asyncio**: Async support for MCP protocol

### Development Dependencies
- **pytest**: Testing framework
- **build**: Package building
- **twine**: PyPI uploading
- **black/isort**: Code formatting

## MCP Client Integration

This server is designed for integration with MCP-compatible AI clients:

### Claude Code Integration

**Method 1: Command Line (Recommended)**
```bash
# Add MCP server to Claude Code
claude mcp add kicad-sch -- python -m mcp_kicad_sch_api

# Add with verbose logging
claude mcp add kicad-sch-verbose --env DEBUG=1 -- python -m mcp_kicad_sch_api -vv

# Verify server is added
claude mcp list
```

**Method 2: JSON Configuration**
```json
// In Claude Code .mcp.json file
{
  "mcpServers": {
    "kicad-sch": {
      "command": "python",
      "args": ["-m", "mcp_kicad_sch_api"],
      "env": {}
    }
  }
}
```

### MCP Client Testing
```bash
# Test server integration with Claude Code
# 1. Add server: claude mcp add kicad-sch -- python -m mcp_kicad_sch_api
# 2. In Claude Code session, tools will be available automatically
# 3. Test with: "Create a blank KiCAD schematic"

# Manual verification that server starts
python -m mcp_kicad_sch_api &
# Should start and wait for MCP protocol communication
```

## Debugging & Development

### Common Issues
1. **Import Errors**: Ensure `kicad-sch-api` submodule is properly installed
2. **MCP Protocol Errors**: Check tool schemas match function signatures  
3. **KiCAD API Errors**: Verify parameters match expected kicad-sch-api format
4. **File Path Issues**: Use absolute paths for schematic file operations

### Debug Logging
```bash
# Enable verbose MCP server logging
python -m mcp_kicad_sch_api -vv

# MCP servers log to stderr by default, not files
# To capture logs:
python -m mcp_kicad_sch_api -vv 2> server.log

# Or run with logging to see real-time output
python -m mcp_kicad_sch_api -vv
```

### Testing New Tools
1. **Add tool definition** to `list_tools()` with proper JSON schema
2. **Implement handler logic** in `handle_call_tool()` dispatcher  
3. **Add integration test** in `test_mcp_server_integration.py`
4. **Test with real MCP client** (Claude Code, etc.)

## Release Process

### Version Management
- **Patch releases** (0.2.x): Bug fixes, minor improvements
- **Minor releases** (0.x.0): New tools, enhanced functionality  
- **Major releases** (x.0.0): Breaking changes, major rewrites

### Release Workflow
```bash
# 1. Update version in pyproject.toml and __init__.py
# 2. Run all tests
pytest tests/ -v

# 3. Build and test package
python -m build
python -m twine check dist/*

# 4. Upload to PyPI
python -m twine upload dist/mcp_kicad_sch_api-X.Y.Z*

# 5. Create git tag
git tag vX.Y.Z
git push origin main --tags
```

## Related Projects

- **[kicad-sch-api](https://github.com/circuit-synth/kicad-sch-api)**: Core KiCAD manipulation library (submodule)
- **[circuit-synth](https://github.com/circuit-synth)**: Parent organization for circuit design automation
- **[Claude Code](https://claude.ai/code)**: Primary MCP client for development

---

*This MCP server enables AI agents to create and manipulate KiCAD schematic files programmatically.*