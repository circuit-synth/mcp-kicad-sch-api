"""Tests for MCP KiCAD Schematic API Server"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from mcp_kicad_sch_api.server import main


@pytest.mark.asyncio
async def test_server_import():
    """Test that server module imports correctly."""
    from mcp_kicad_sch_api import server
    assert hasattr(server, 'main')


@pytest.mark.asyncio  
async def test_create_schematic():
    """Test schematic creation functionality."""
    # This would require mocking kicad_sch_api
    # For now, just test the import works
    with patch('mcp_kicad_sch_api.server.ksa') as mock_ksa:
        mock_schematic = MagicMock()
        mock_ksa.create_schematic.return_value = mock_schematic
        
        # Test would go here - currently just checking imports work
        assert mock_ksa is not None


def test_module_version():
    """Test module has version."""
    from mcp_kicad_sch_api import __version__
    assert __version__ == "0.1.0"


def test_main_import():
    """Test main function can be imported."""
    from mcp_kicad_sch_api import main
    assert callable(main)