"""MCP KiCAD Schematic API Server Implementation

Standard MCP server providing KiCAD schematic manipulation tools.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional, Tuple
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import the KiCAD schematic API
try:
    import kicad_sch_api as ksa
except ImportError as e:
    print(f"Error: Could not import kicad-sch-api: {e}", file=sys.stderr)
    print("Please install: pip install kicad-sch-api", file=sys.stderr)
    sys.exit(1)

# Configure logging to stderr (not stdout for MCP)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global schematic instance
current_schematic: Optional[Any] = None


async def main():
    """Main MCP server entry point."""
    logger.info("Starting MCP KiCAD Schematic API Server...")
    
    server = Server("mcp-kicad-sch-api")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available KiCAD schematic tools."""
        return [
            Tool(
                name="create_schematic",
                description="Create a new KiCAD schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name for the schematic"}
                    },
                    "additionalProperties": False
                }
            ),
            Tool(
                name="load_schematic", 
                description="Load an existing KiCAD schematic file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the .kicad_sch file"}
                    },
                    "required": ["file_path"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="save_schematic",
                description="Save the current schematic to a file", 
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Optional path to save to"}
                    },
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_component",
                description="Add a component to the current schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "lib_id": {"type": "string", "description": "Library ID (e.g., Device:R)"},
                        "reference": {"type": "string", "description": "Component reference (e.g., R1)"},
                        "value": {"type": "string", "description": "Component value (e.g., 10k)"},
                        "position": {"type": "array", "items": {"type": "number"}, "description": "[x, y] coordinates"},
                        "properties": {"type": "string", "description": "Additional properties as key=value pairs"}
                    },
                    "required": ["lib_id", "reference", "value", "position"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="search_components",
                description="Search for components in KiCAD symbol libraries",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string", "description": "Search term (e.g., resistor, op amp, 555)"},
                        "library": {"type": "string", "description": "Optional library to search in"},
                        "limit": {"type": "integer", "description": "Maximum number of results"}
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_wire",
                description="Add a wire connection between two points",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_pos": {"type": "array", "items": {"type": "number"}, "description": "[x, y] start coordinates"},
                        "end_pos": {"type": "array", "items": {"type": "number"}, "description": "[x, y] end coordinates"}
                    },
                    "required": ["start_pos", "end_pos"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="list_components",
                description="List all components in the current schematic",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="get_schematic_info", 
                description="Get information about the current schematic",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            )
        ]
    
    @server.call_tool()
    async def create_schematic(name: str = "untitled") -> List[TextContent]:
        """Create a new KiCAD schematic.
        
        Args:
            name: Name for the schematic
            
        Returns:
            Status message about schematic creation
        """
        global current_schematic
        
        try:
            logger.info(f"Creating new schematic: {name}")
            current_schematic = ksa.create_schematic(name)
            
            return [TextContent(
                type="text",
                text=f"✅ Created new KiCAD schematic: '{name}'"
            )]
        except Exception as e:
            logger.error(f"Error creating schematic: {e}")
            return [TextContent(
                type="text", 
                text=f"❌ Error creating schematic: {str(e)}"
            )]
    
    @server.call_tool()
    async def load_schematic(file_path: str) -> List[TextContent]:
        """Load an existing KiCAD schematic file.
        
        Args:
            file_path: Path to the .kicad_sch file
            
        Returns:
            Status message about schematic loading
        """
        global current_schematic
        
        try:
            logger.info(f"Loading schematic: {file_path}")
            current_schematic = ksa.load_schematic(file_path)
            
            return [TextContent(
                type="text",
                text=f"✅ Loaded KiCAD schematic: '{file_path}'"
            )]
        except Exception as e:
            logger.error(f"Error loading schematic: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error loading schematic: {str(e)}"
            )]
    
    @server.call_tool()
    async def save_schematic(file_path: Optional[str] = None) -> List[TextContent]:
        """Save the current schematic to a file.
        
        Args:
            file_path: Optional path to save to (uses current if not provided)
            
        Returns:
            Status message about schematic saving
        """
        if current_schematic is None:
            return [TextContent(
                type="text",
                text="❌ No schematic loaded. Create or load a schematic first."
            )]
        
        try:
            if file_path:
                current_schematic.save(file_path)
                logger.info(f"Saved schematic to: {file_path}")
                return [TextContent(
                    type="text",
                    text=f"✅ Saved schematic to: {file_path}"
                )]
            else:
                current_schematic.save()
                logger.info("Saved schematic to current file")
                return [TextContent(
                    type="text", 
                    text="✅ Saved schematic to current file"
                )]
        except Exception as e:
            logger.error(f"Error saving schematic: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error saving schematic: {str(e)}"
            )]
    
    @server.call_tool()
    async def add_component(
        lib_id: str,
        reference: str,
        value: str, 
        position: List[float],
        properties: str = ""
    ) -> List[TextContent]:
        """Add a component to the current schematic.
        
        Args:
            lib_id: Library ID (e.g., "Device:R" for resistor)
            reference: Component reference (e.g., "R1")
            value: Component value (e.g., "10k")
            position: [x, y] position coordinates
            properties: Additional properties as key=value pairs
            
        Returns:
            Status message about component addition
        """
        if current_schematic is None:
            return [TextContent(
                type="text",
                text="❌ No schematic loaded. Create or load a schematic first."
            )]
        
        if len(position) != 2:
            return [TextContent(
                type="text",
                text="❌ Position must be [x, y] coordinates"
            )]
        
        try:
            logger.info(f"Adding component: {lib_id} {reference}={value} at {position}")
            
            component = current_schematic.components.add(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=tuple(position)
            )
            
            # Add additional properties if provided
            if properties:
                for prop in properties.split(","):
                    if "=" in prop:
                        key, val = prop.strip().split("=", 1)
                        component.set_property(key.strip(), val.strip())
            
            return [TextContent(
                type="text",
                text=f"✅ Added component: {reference} ({lib_id}) = {value} at {position}"
            )]
        except Exception as e:
            logger.error(f"Error adding component: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error adding component: {str(e)}"
            )]
    
    @server.call_tool()
    async def search_components(
        query: str,
        library: Optional[str] = None,
        limit: int = 20
    ) -> List[TextContent]:
        """Search for components in KiCAD symbol libraries.
        
        Args:
            query: Search term (e.g., "resistor", "op amp", "555")
            library: Optional library to search in
            limit: Maximum number of results
            
        Returns:
            List of matching components
        """
        try:
            logger.info(f"Searching components: {query}")
            
            # Use the kicad-sch-api search functionality
            from kicad_sch_api.discovery.search_index import search_components as search_func
            
            results = search_func(query, library=library, limit=limit)
            
            if not results:
                return [TextContent(
                    type="text",
                    text=f"No components found matching '{query}'"
                )]
            
            result_text = f"Found {len(results)} components matching '{query}':\n\n"
            for result in results[:limit]:
                result_text += f"• {result.get('lib_id', 'Unknown')}"
                if 'description' in result:
                    result_text += f" - {result['description']}"
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error searching components: {str(e)}"
            )]
    
    @server.call_tool()
    async def add_wire(
        start_pos: List[float],
        end_pos: List[float]
    ) -> List[TextContent]:
        """Add a wire connection between two points.
        
        Args:
            start_pos: [x, y] start coordinates
            end_pos: [x, y] end coordinates
            
        Returns:
            Status message about wire addition
        """
        if current_schematic is None:
            return [TextContent(
                type="text",
                text="❌ No schematic loaded. Create or load a schematic first."
            )]
        
        if len(start_pos) != 2 or len(end_pos) != 2:
            return [TextContent(
                type="text", 
                text="❌ Positions must be [x, y] coordinates"
            )]
        
        try:
            logger.info(f"Adding wire from {start_pos} to {end_pos}")
            
            current_schematic.add_wire(
                start=tuple(start_pos),
                end=tuple(end_pos)
            )
            
            return [TextContent(
                type="text",
                text=f"✅ Added wire from {start_pos} to {end_pos}"
            )]
        except Exception as e:
            logger.error(f"Error adding wire: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error adding wire: {str(e)}"
            )]
    
    @server.call_tool()
    async def list_components() -> List[TextContent]:
        """List all components in the current schematic.
        
        Returns:
            List of components with details
        """
        if current_schematic is None:
            return [TextContent(
                type="text",
                text="❌ No schematic loaded. Create or load a schematic first."
            )]
        
        try:
            components = current_schematic.components.list()
            
            if not components:
                return [TextContent(
                    type="text",
                    text="No components in the current schematic."
                )]
            
            result_text = f"Components in schematic ({len(components)} total):\n\n"
            for comp in components:
                result_text += f"• {comp.reference} ({comp.lib_id}) = {comp.value}"
                if hasattr(comp, 'position'):
                    result_text += f" at {comp.position}"
                result_text += "\n"
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error listing components: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error listing components: {str(e)}"
            )]
    
    @server.call_tool()
    async def get_schematic_info() -> List[TextContent]:
        """Get information about the current schematic.
        
        Returns:
            Schematic information and statistics
        """
        if current_schematic is None:
            return [TextContent(
                type="text",
                text="❌ No schematic loaded. Create or load a schematic first."
            )]
        
        try:
            info = current_schematic.get_info()
            
            info_text = "📋 Schematic Information:\n\n"
            info_text += f"• Title: {info.get('title', 'Untitled')}\n"
            info_text += f"• Components: {info.get('component_count', 0)}\n"
            info_text += f"• Wires: {info.get('wire_count', 0)}\n"
            info_text += f"• Sheets: {info.get('sheet_count', 0)}\n"
            
            if 'version' in info:
                info_text += f"• Version: {info['version']}\n"
            
            return [TextContent(type="text", text=info_text)]
            
        except Exception as e:
            logger.error(f"Error getting schematic info: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error getting schematic info: {str(e)}"
            )]
    
    # Start the MCP server
    logger.info("MCP server ready, waiting for connections...")
    
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options,
            raise_exceptions=True
        )


if __name__ == "__main__":
    asyncio.run(main())