#!/usr/bin/env python3
"""Simple test to validate MCP server can be imported and basic functionality works."""

import sys
import asyncio

def test_imports():
    """Test that all imports work correctly."""
    try:
        import mcp_kicad_sch_api
        print("✅ mcp_kicad_sch_api imports successfully")
        
        from mcp_kicad_sch_api import main
        print("✅ main function available")
        
        from mcp_kicad_sch_api.server import main as server_main
        print("✅ server.main function available")
        
        import kicad_sch_api
        print("✅ kicad_sch_api dependency available")
        
        from mcp.server import Server
        print("✅ MCP SDK available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_kicad_api():
    """Test that KiCAD API functions work."""
    try:
        import kicad_sch_api as ksa
        
        # Test schematic creation
        sch = ksa.create_schematic("test")
        print("✅ Can create schematic")
        
        # Test component addition
        sch.components.add(
            lib_id="Device:R",
            reference="R1", 
            value="10k",
            position=(100, 100)
        )
        print("✅ Can add components")
        
        return True
        
    except Exception as e:
        print(f"❌ KiCAD API error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing MCP KiCAD Schematic API Server...")
    print()
    
    success = True
    
    print("Test 1: Import validation")
    success &= test_imports()
    print()
    
    print("Test 2: KiCAD API functionality")
    success &= test_kicad_api()
    print()
    
    if success:
        print("🎉 All tests passed! MCP server is ready.")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())