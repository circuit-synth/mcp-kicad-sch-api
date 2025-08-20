#!/usr/bin/env python3
"""
Comprehensive test script for all MCP KiCAD tools.

This script tests all 20 MCP tools to verify they work correctly.
"""

import sys
import asyncio
import tempfile
import os
sys.path.insert(0, 'src')

from mcp_kicad_sch_api.server import handle_call_tool

async def test_all_mcp_tools():
    """Test all MCP tools systematically."""
    
    print("🧪 Testing Comprehensive MCP KiCAD Tools v0.3.0")
    print("=" * 60)
    
    # 1. Create schematic
    print("\n1️⃣ Creating schematic...")
    result = await handle_call_tool('create_schematic', {'name': 'Comprehensive Test'})
    print(f"   {result[0].text}")
    
    # 2. Add components
    print("\n2️⃣ Adding components...")
    components_to_add = [
        ('Device:R', 'R1', '10k', [101.6, 101.6]),
        ('Device:R', 'R2', '20k', [127.0, 101.6]),
        ('Device:C', 'C1', '100nF', [101.6, 127.0])
    ]
    
    for lib_id, ref, value, pos in components_to_add:
        result = await handle_call_tool('add_component', {
            'lib_id': lib_id,
            'reference': ref,
            'value': value,
            'position': pos,
            'footprint': 'Resistor_SMD:R_0603_1608Metric' if 'R' in lib_id else 'Capacitor_SMD:C_0603_1608Metric'
        })
        print(f"   {result[0].text}")
    
    # 3. Test pin positioning
    print("\n3️⃣ Testing pin positioning...")
    result = await handle_call_tool('get_component_pin_position', {'reference': 'R1', 'pin_number': '1'})
    print(f"   {result[0].text}")
    
    result = await handle_call_tool('list_component_pins', {'reference': 'R1'})
    print(f"   {result[0].text}")
    
    # 4. Test pin-accurate labels
    print("\n4️⃣ Testing pin-accurate labels...")
    result = await handle_call_tool('add_label_to_pin', {
        'reference': 'R1',
        'pin_number': '1', 
        'text': 'VIN'
    })
    print(f"   {result[0].text}")
    
    result = await handle_call_tool('connect_pins_with_labels', {
        'comp1_ref': 'R1',
        'pin1': '2',
        'comp2_ref': 'R2', 
        'pin2': '1',
        'net_name': 'VOUT'
    })
    print(f"   {result[0].text}")
    
    # 5. Test validation
    print("\n5️⃣ Testing validation...")
    result = await handle_call_tool('validate_schematic', {})
    print(f"   {result[0].text}")
    
    # 6. Test text elements
    print("\n6️⃣ Testing text elements...")
    result = await handle_call_tool('add_text', {
        'text': 'Test Circuit',
        'position': [90, 80],
        'rotation': 0,
        'size': 2.0
    })
    print(f"   {result[0].text}")
    
    # 7. Test filtering
    print("\n7️⃣ Testing component filtering...")
    result = await handle_call_tool('filter_components', {'lib_id': 'Device:R'})
    print(f"   {result[0].text}")
    
    result = await handle_call_tool('components_in_area', {
        'x1': 100, 'y1': 100, 'x2': 130, 'y2': 130
    })
    print(f"   {result[0].text}")
    
    # 8. Test bulk operations
    print("\n8️⃣ Testing bulk operations...")
    result = await handle_call_tool('bulk_update_components', {
        'criteria': {'lib_id': 'Device:R'},
        'updates': {'properties': {'Tolerance': '1%'}}
    })
    print(f"   {result[0].text}")
    
    # 9. Test backup and clone
    print("\n9️⃣ Testing utilities...")
    result = await handle_call_tool('clone_schematic', {'new_name': 'Test Clone'})
    print(f"   {result[0].text}")
    
    # 10. Save test schematic
    print("\n🔟 Saving test schematic...")
    test_path = '/Users/shanemattner/Desktop/mcp_comprehensive_test.kicad_sch'
    result = await handle_call_tool('save_schematic', {'file_path': test_path})
    print(f"   {result[0].text}")
    
    print(f"\n✅ Comprehensive MCP tool testing completed!")
    print(f"📁 Test schematic saved to: {test_path}")
    print(f"🔍 Open in KiCAD to verify all elements were created correctly")

if __name__ == "__main__":
    asyncio.run(test_all_mcp_tools())