# PRD: Pin-Accurate Connections for KiCAD Schematics (Labels & Wires)

## Problem Statement

Current KiCAD schematic generation has critical connectivity issues:

1. **Incorrect Label Placement**: Labels are placed at arbitrary positions instead of actual pin locations, causing no electrical connections
2. **Incorrect Wire Placement**: Wires drawn to arbitrary positions instead of actual pin endpoints, causing connection failures
3. **Missing Pin Geometry**: No way to calculate absolute pin positions accounting for component rotation/mirroring  
4. **Power Symbol Redundancy**: Redundant labels placed on power symbols that already have built-in text
5. **No Connection Validation**: No way to verify labels or wires create proper electrical connections

**Result**: Generated schematics have components that appear connected but have no actual electrical connectivity, whether using labels OR wires.

## Proposed Solution

Implement comprehensive pin-accurate connections (both labels AND wires) by porting proven logic from circuit-synth:

### **Phase 1: Base Library Enhancement (kicad-sch-api)**
- Add pin position calculation with transformation support
- Implement smart label positioning algorithms
- **Add pin-to-pin wire routing capabilities**
- Add component geometry and symbol parsing capabilities
- Port proven circuit-synth functions to base library

### **Phase 2: MCP Server Integration (mcp-kicad-sch-api)**  
- Add new MCP tools for pin-based operations (labels AND wires)
- Enhance existing tools with pin intelligence
- **Add pin-to-pin wire drawing tools**
- Implement connection validation and verification
- Add power symbol detection and handling

## Architecture Decision: Logic Migration Strategy

**Migration from circuit-synth to kicad-sch-api** ✅ **RECOMMENDED**
- **Extract and refactor** pin positioning logic from circuit-synth
- **Improve and modernize** the implementation during migration
- **Make kicad-sch-api the authoritative source** for KiCAD manipulation
- **Update circuit-synth to depend on kicad-sch-api** instead of maintaining duplicate logic
- **Create cleaner, more maintainable APIs** in the process

**Benefits of Migration:**
- Single source of truth for KiCAD schematic manipulation
- Reduced code duplication across repositories
- Better testing and maintenance of core functionality
- circuit-synth becomes lighter and more focused on high-level workflows

**Decision**: **Migrate** the pin positioning logic from circuit-synth to kicad-sch-api, then update circuit-synth to use the new API.

## Technical Implementation

### **Base Library Changes (kicad-sch-api)**

#### **New Core Functions:**
```python
# In kicad_sch_api/core/schematic.py
def get_component_pin_position(self, reference: str, pin_number: str) -> Optional[Point]:
    """Get absolute position of component pin with transformations."""
    
def add_label_to_pin(self, reference: str, pin_number: str, text: str, offset: float = 0) -> str:
    """Add label directly to component pin location."""
    
def connect_pins_with_labels(self, comp1_ref: str, pin1: str, comp2_ref: str, pin2: str, net_name: str) -> List[str]:
    """Connect two component pins using same net label."""

def connect_pins_with_wire(self, comp1_ref: str, pin1: str, comp2_ref: str, pin2: str) -> str:
    """Draw wire directly between two component pins."""
    
def add_wire_to_pin(self, start_pos: Point, comp_ref: str, pin_number: str) -> str:
    """Draw wire from arbitrary position to specific component pin."""
```

#### **Enhanced Component Support:**
```python
# Enhanced add_component with geometry support
def add_component(self, lib_id: str, reference: str, value: str, position: Point, 
                  rotation: float = 0, mirror: str = None, footprint: str = None) -> Component:
    """Add component with full transformation support."""
```

#### **Functions to Migrate from Circuit-Synth:**
1. **`get_pin_position()`** from `connection_utils.py:99-141` → Extract to `kicad_sch_api/core/pin_utils.py`
2. **`apply_transformation()`** from `connection_utils.py:61-97` → Extract to `kicad_sch_api/core/geometry.py`
3. **`calculate_label_position()`** from `geometry_utils.py:163-187` → Extract to `kicad_sch_api/core/label_positioning.py`
4. **`calculate_label_orientation()`** from `geometry_utils.py:190-229` → Extract to `kicad_sch_api/core/label_positioning.py` ⭐ **CRITICAL**
5. **`suggest_label_for_component_pin()`** from `label_utils.py:247-303` → Extract to `kicad_sch_api/core/label_positioning.py`
6. **`transform_pin_to_world()`** coordinate conversion → Extract to `kicad_sch_api/core/geometry.py`

#### **Migration Benefits:**
- **Cleaner APIs**: Refactor during migration for better usability
- **Better Testing**: Comprehensive test suite in kicad-sch-api
- **Reduced Duplication**: Single source of truth for pin logic
- **Improved Documentation**: Better API docs and examples

#### **Pin Orientation Logic (CRITICAL):**
From circuit-synth analysis, labels must be positioned based on pin direction:
- **Pin pointing right (0°)** → Label placed to the **right** of pin with **0° orientation**
- **Pin pointing up (90°)** → Label placed **above** pin with **90° orientation**  
- **Pin pointing left (180°)** → Label placed to the **left** of pin with **180° orientation**
- **Pin pointing down (270°)** → Label placed **below** pin with **270° orientation**

**Key Algorithm**: 
```python
# From geometry_utils.py:209-229
world_orientation = (pin.orientation + symbol_rotation) % 360
opposite_orientation = (world_orientation + 180) % 360  # Label points AWAY from component
```

This ensures labels are readable and positioned logically relative to pin direction.

### **MCP Server Changes (mcp-kicad-sch-api)**

#### **New MCP Tools:**
```python
# New MCP tools for pin operations
- get_component_pin_position(reference: str, pin_number: str) -> position
- add_label_to_pin(reference: str, pin_number: str, text: str) -> label_uuid  
- connect_pins_with_labels(comp1_ref: str, pin1: str, comp2_ref: str, pin2: str, net_name: str) -> connection_info
- connect_pins_with_wire(comp1_ref: str, pin1: str, comp2_ref: str, pin2: str) -> wire_uuid
- add_wire_to_pin(start_pos: [x,y], comp_ref: str, pin_number: str) -> wire_uuid
- list_component_pins(reference: str) -> pin_list
```

#### **Enhanced Existing Tools:**
```python
# Enhanced add_component with rotation support
- add_component(lib_id, reference, value, position, rotation?, mirror?, footprint?) -> component_info

# Smart add_label that detects power symbols  
- add_label(text, position, auto_pin_detect?) -> label_uuid
```

## Success Criteria

### **Functional Requirements:**
1. ✅ Labels placed exactly on pin connection points
2. ✅ **Pin orientation determines label direction and placement** ⭐ **CRITICAL**
3. ✅ Component rotation and mirroring properly handled in pin calculations
4. ✅ Power symbols don't get redundant labels
5. ✅ Generated schematics have proper electrical connectivity
6. ✅ Pin positions calculated accurately from symbol definitions
7. ✅ Label text orientation matches pin direction for readability

### **Technical Requirements:**
1. ✅ Port circuit-synth pin positioning logic to base library
2. ✅ Add comprehensive pin geometry calculation  
3. ✅ Implement transformation math (rotation, mirroring)
4. ✅ Add MCP tools for pin-based operations
5. ✅ Maintain backward compatibility with existing MCP tools

### **Validation Tests:**
1. ✅ Create voltage divider with proper pin connections
2. ✅ Verify labels create electrical connectivity in KiCAD
3. ✅ **Test pin orientation scenarios**: right/up/left/down pointing pins ⭐ **CRITICAL**
4. ✅ Test component rotation scenarios (0°, 90°, 180°, 270°) with pin orientation preservation
5. ✅ Validate power symbol handling doesn't create duplicate labels
6. ✅ **Verify label readability**: text orientation matches pin direction
7. ✅ Round-trip test: save → load → verify connectivity

## Implementation Plan

### **Phase 1: Logic Migration to Base Library (Estimated: 3-4 hours)**
1. **Extract logic from circuit-synth**: Copy relevant functions to kicad-sch-api
2. **Refactor and improve**: Clean up APIs, add better type hints, improve documentation
3. **Add new modules**: Create `pin_utils.py`, `geometry.py`, `label_positioning.py`
4. **Integrate with existing Schematic class**: Add new methods for pin operations
5. **Create comprehensive tests**: Test pin positioning, transformations, label placement
6. **Update circuit-synth**: Modify circuit-synth to import from kicad-sch-api instead of local logic

### **Phase 2: MCP Server (Estimated: 1-2 hours)**
1. Add new MCP tools for pin operations
2. Enhance existing tools with pin intelligence
3. Update tool schemas and documentation  
4. Add integration tests for pin-based workflows
5. Update version and release to PyPI

### **Phase 3: Validation (Estimated: 1 hour)**
1. Test with real voltage divider circuit
2. Verify electrical connectivity in KiCAD
3. Validate against multiple component types
4. Performance testing with complex circuits

## Risk Assessment

### **Low Risk:**
- Circuit-synth logic is proven and tested
- Base library changes are additive (no breaking changes)
- Pin positioning is well-understood domain

### **Medium Risk:**
- Symbol library compatibility across different KiCAD versions
- Component transformation edge cases (complex rotations)

### **Mitigation Strategies:**
- Comprehensive test suite with real KiCAD projects
- Gradual rollout with backward compatibility
- Extensive validation against circuit-synth reference implementations

## Dependencies

- ✅ Circuit-synth codebase available as submodule
- ✅ Existing kicad-sch-api has component and label infrastructure
- ✅ MCP server has working tool dispatch system
- ✅ Symbol cache system exists for geometry lookups

## Success Metrics

1. **Connectivity Test**: 100% of generated labels create electrical connections in KiCAD
2. **Position Accuracy**: Pin positions within 0.01mm of expected values  
3. **Power Symbol Intelligence**: Zero redundant labels on power symbols
4. **Transformation Support**: All rotation/mirror combinations work correctly
5. **Performance**: Pin position calculation <10ms per component

## Migration Impact

### **Repositories Affected:**
1. **kicad-sch-api**: Gets new pin positioning and label logic (⬆️ Enhanced)
2. **mcp-kicad-sch-api**: Gets new MCP tools using migrated logic (⬆️ Enhanced)  
3. **circuit-synth**: Removes duplicate logic, imports from kicad-sch-api (🔄 Simplified)

### **Benefits:**
- **Single Source of Truth**: Pin logic centralized in kicad-sch-api
- **Better Maintenance**: Easier to update and test core functionality
- **Reduced Complexity**: circuit-synth becomes lighter and more focused
- **Improved APIs**: Migration allows for API improvements and modernization

---

**Total Estimated Time**: 5-7 hours (includes migration effort)  
**Priority**: High (Critical for usable schematic generation + repo consolidation)  
**Recommended Approach**: Migrate logic to base library, update both MCP server and circuit-synth to use it

Please review this PRD and let me know if you'd like me to proceed with implementation or if you have any feedback/changes.