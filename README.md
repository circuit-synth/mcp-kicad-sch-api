# MCP KiCAD Schematic API

Model Context Protocol (MCP) server providing KiCAD schematic manipulation tools for AI agents.

## Overview

This MCP server exposes the [`kicad-sch-api`](https://github.com/circuit-synth/kicad-sch-api) library as tools that AI agents can use to create, modify, and analyze KiCAD schematic files.

## Features

- 🔧 **Create Schematics**: Generate new KiCAD schematic files
- ⚡ **Add Components**: Place resistors, capacitors, ICs, and more
- 🔍 **Search Components**: Find parts in KiCAD symbol libraries  
- 🔗 **Add Connections**: Create wires and nets
- 📐 **Hierarchical Design**: Support for hierarchical sheets and labels
- 🎯 **Format Preservation**: Maintains exact KiCAD file format compatibility

## Quick Start

### Installation

```bash
pip install mcp-kicad-sch-api
```

### Configuration

#### Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "python",
      "args": ["-m", "mcp_kicad_sch_api"],
      "env": {}
    }
  }
}
```

#### Claude Code
```bash
claude mcp add kicad-sch-api --scope user -- python -m mcp_kicad_sch_api
```

#### Other MCP Clients
The server supports standard MCP stdio transport and should work with any MCP-compatible client.

## Usage Examples

Ask your AI agent:

- *"Create a voltage divider circuit with two 10kΩ resistors"*
- *"Add an Arduino Nano to the schematic at position (100, 100)"*
- *"Search for operational amplifiers in the KiCAD libraries"*
- *"Create a hierarchical sheet for the power supply section"*

## Tools Available

| Tool | Description |
|------|-------------|
| `create_schematic` | Create a new KiCAD schematic file |
| `add_component` | Add components (resistors, capacitors, ICs, etc.) |
| `search_components` | Search KiCAD symbol libraries |
| `add_wire` | Create wire connections |
| `add_hierarchical_sheet` | Add hierarchical design sheets |
| `add_sheet_pin` | Add pins to hierarchical sheets |
| `add_hierarchical_label` | Add hierarchical labels |
| `list_components` | List all components in schematic |
| `get_schematic_info` | Get schematic information |

## Requirements

- Python 3.10+
- KiCAD (for symbol libraries)
- [`kicad-sch-api`](https://pypi.org/project/kicad-sch-api/) library

## Development

```bash
git clone https://github.com/circuit-synth/mcp-kicad-sch-api.git
cd mcp-kicad-sch-api
uv sync --dev
uv run python -m mcp_kicad_sch_api
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Related Projects

- [`kicad-sch-api`](https://github.com/circuit-synth/kicad-sch-api) - Core Python library
- [`circuit-synth`](https://github.com/circuit-synth/circuit-synth) - AI-powered circuit design platform

---

🤖 **AI-Powered Circuit Design Made Easy**