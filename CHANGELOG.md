# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-19

### Added
- Initial release of MCP KiCAD Schematic API server
- Standard MCP server implementation using official MCP SDK
- Support for schematic creation and loading
- Component addition with library search
- Wire connections and basic routing
- Hierarchical sheet support
- Cross-platform MCP client compatibility (Claude Desktop, Claude Code, etc.)
- Comprehensive tool set for KiCAD schematic manipulation

### Features
- `create_schematic` - Create new KiCAD schematic files
- `load_schematic` - Load existing schematic files  
- `save_schematic` - Save schematics to disk
- `add_component` - Add electronic components (resistors, capacitors, ICs, etc.)
- `search_components` - Search KiCAD symbol libraries
- `add_wire` - Create wire connections between components
- `list_components` - List all components in current schematic
- `get_schematic_info` - Get schematic metadata and statistics

### Technical
- Built on standard MCP SDK for maximum compatibility
- Depends on `kicad-sch-api` library for core functionality
- Async/await support for responsive AI agent interactions
- Comprehensive error handling and logging
- Type hints and documentation for all tools