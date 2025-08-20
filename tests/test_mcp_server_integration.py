#!/usr/bin/env python3
"""
Integration tests for MCP KiCAD Schematic API Server

Tests basic functionality to prevent regression issues.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_kicad_sch_api.server import handle_call_tool
import kicad_sch_api as ksa


class TestMCPServerIntegration:
    """Test the MCP server integration with real KiCAD API."""
    
    @pytest.fixture
    def temp_schematic_file(self):
        """Create a temporary schematic file path."""
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_create_schematic(self):
        """Test creating a new schematic."""
        # Import the server module to get access to the handler
        from mcp_kicad_sch_api.server import main
        import importlib
        
        # We need to simulate the handler function
        # For now, test the basic API directly
        sch = ksa.create_schematic("Test Circuit")
        assert sch is not None
        summary = sch.get_summary()
        assert summary["title"] == "Test Circuit"
    
    @pytest.mark.asyncio
    async def test_add_component_workflow(self):
        """Test the complete component addition workflow."""
        # Create schematic
        sch = ksa.create_schematic("Component Test")
        
        # Add a resistor
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1", 
            value="10k",
            position=(100, 100),
            footprint="Resistor_SMD:R_0603_1608Metric"
        )
        
        assert resistor.reference == "R1"
        assert resistor.value == "10k"
        assert resistor.lib_id == "Device:R"
        assert resistor.position.x == 100
        assert resistor.position.y == 100
        
        # Verify component is in schematic
        components = list(sch.components)
        assert len(components) == 1
        assert components[0].reference == "R1"
    
    @pytest.mark.asyncio
    async def test_add_wire_workflow(self):
        """Test wire addition workflow."""
        # Create schematic
        sch = ksa.create_schematic("Wire Test")
        
        # Add a wire
        wire_uuid = sch.add_wire(
            start=(50, 50),
            end=(100, 50)
        )
        
        assert wire_uuid is not None
        assert len(wire_uuid) > 0  # Should be a UUID string
        
        # Verify wire exists
        assert len(sch.wires) == 1
        wire = list(sch.wires)[0]
        assert wire.start.x == 50
        assert wire.start.y == 50
        assert wire.end.x == 100
        assert wire.end.y == 50
    
    @pytest.mark.asyncio
    async def test_add_label_workflow(self):
        """Test label addition workflow."""
        # Create schematic
        sch = ksa.create_schematic("Label Test")
        
        # Add a label
        label_uuid = sch.add_label(
            text="VCC",
            position=(75, 75),
            rotation=0.0,
            size=1.27
        )
        
        assert label_uuid is not None
        assert len(label_uuid) > 0  # Should be a UUID string
    
    @pytest.mark.asyncio 
    async def test_save_and_load_workflow(self, temp_schematic_file):
        """Test saving and loading schematic files."""
        # Create and populate schematic
        sch = ksa.create_schematic("Save Test")
        
        # Add some content
        sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="1k", 
            position=(50, 50)
        )
        
        sch.add_wire(start=(40, 50), end=(60, 50))
        sch.add_label(text="TEST", position=(50, 40))
        
        # Save schematic
        sch.save(temp_schematic_file)
        assert os.path.exists(temp_schematic_file)
        assert os.path.getsize(temp_schematic_file) > 100  # Should have content
        
        # Load schematic
        sch2 = ksa.load_schematic(temp_schematic_file)
        assert sch2 is not None
        
        # Verify content
        components = list(sch2.components)
        assert len(components) == 1
        assert components[0].reference == "R1"
        assert components[0].value == "1k"
        
        # Verify wires exist
        assert len(sch2.wires) == 1
    
    @pytest.mark.asyncio
    async def test_component_properties(self):
        """Test setting component properties."""
        sch = ksa.create_schematic("Properties Test")
        
        # Add component
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 100)
        )
        
        # Set properties
        resistor.set_property("MPN", "RC0603FR-0710KL")
        resistor.set_property("Tolerance", "1%")
        resistor.set_property("Power", "0.1W")
        
        # Verify properties
        assert resistor.get_property("MPN") == "RC0603FR-0710KL"
        assert resistor.get_property("Tolerance") == "1%"
        assert resistor.get_property("Power") == "0.1W"
    
    @pytest.mark.asyncio
    async def test_hierarchical_labels(self):
        """Test hierarchical label functionality.""" 
        sch = ksa.create_schematic("Hierarchical Test")
        
        # Import the shape enum
        from kicad_sch_api.core.types import HierarchicalLabelShape
        
        # Add hierarchical label
        label_uuid = sch.add_hierarchical_label(
            text="DATA_BUS",
            position=(100, 100),
            shape=HierarchicalLabelShape.BIDIRECTIONAL,
            rotation=0.0,
            size=1.27
        )
        
        assert label_uuid is not None
        assert len(label_uuid) > 0
    
    @pytest.mark.asyncio
    async def test_junction_functionality(self):
        """Test junction (connection point) functionality."""
        sch = ksa.create_schematic("Junction Test")
        
        # Add junction
        junction_uuid = sch.junctions.add(
            position=(50, 50),
            diameter=0.0
        )
        
        assert junction_uuid is not None
        assert len(junction_uuid) > 0
        
        # Verify junction exists
        assert len(sch.junctions) == 1
        junction = list(sch.junctions)[0]
        assert junction.position.x == 50
        assert junction.position.y == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])