# PRD: Pin-Accurate Connections for KiCAD Schematics (Labels & Wires)

## Problem Statement

Current KiCAD schematic generation has critical connectivity issues:

1. **Incorrect Label Placement**: Labels are placed at arbitrary positions instead of actual pin locations, causing no electrical connections
2. **Incorrect Wire Placement**: Wires drawn to arbitrary positions instead of actual pin endpoints, causing connection failures
3. **Missing Pin Geometry**: No way to calculate absolute pin positions accounting for component rotation/mirroring  
4. **Power Symbol Redundancy**: Redundant labels placed on power symbols that already have built-in text
5. **No Connection Validation**: No way to verify labels or wires create proper electrical connections

**Result**: Generated schematics have components that appear connected but have no actual electrical connectivity, whether using labels OR wires.

## Deep Analysis of Circuit-Synth Implementation

### **Critical Discovery: Y-Axis Handling in Pin Transformations**

**ISSUE IDENTIFIED**: Circuit-synth uses a **fundamentally different coordinate transformation** that we missed:

From `geometry_utils.py:77-80`:
```python
# Note: We negate Y here because in symbol definitions, positive Y means "up"
# but in KiCad's world coordinates, positive Y means "down"
rotated_x = pin.position.x * cos_a - (-pin.position.y) * sin_a
rotated_y = pin.position.x * sin_a + (-pin.position.y) * cos_a
```

**Key Insight**: Circuit-synth **NEGATES the pin Y coordinate** during transformation (`-pin.position.y`), but our `apply_transformation` function does NOT.

### **Pin Positioning Workflow Analysis**

#### **Circuit-Synth Workflow:**
1. **Pin Position Calculation** (`geometry_utils.py:19-48`):
   ```python
   def get_actual_pin_position(symbol: SchematicSymbol, pin_number: str) -> Optional[Point]:
       for pin in symbol.pins:
           if pin.number == pin_number:
               world_pos = GeometryUtils.transform_pin_to_world(pin, symbol.position, symbol.rotation)
               return world_pos
   ```

2. **Pin Transformation** (`geometry_utils.py:51-90`):
   ```python
   def transform_pin_to_world(pin: SchematicPin, symbol_pos: Point, symbol_rotation: float) -> Point:
       # CRITICAL: Negates Y coordinate for KiCAD coordinate system
       rotated_x = pin.position.x * cos_a - (-pin.position.y) * sin_a  # Note: -pin.position.y
       rotated_y = pin.position.x * sin_a + (-pin.position.y) * cos_a   # Note: -pin.position.y
       
       world_x = symbol_pos.x + rotated_x
       world_y = symbol_pos.y + rotated_y
       return Point(world_x, world_y)
   ```

3. **Label Positioning** (`geometry_utils.py:163-187`):
   ```python
   def calculate_label_position(pin: SchematicPin, pin_world_pos: Point, symbol_rotation: float, offset_distance: float = 0) -> Point:
       # Place labels at the pin position (where pin connects to component)
       # KiCad will handle the label anchor correctly based on its orientation
       return pin_world_pos  # Simple: just use pin position directly
   ```

4. **Label Orientation** (`geometry_utils.py:190-231`):
   ```python
   def calculate_label_orientation(pin: SchematicPin, symbol_rotation: float) -> float:
       world_orientation = (pin.orientation + symbol_rotation) % 360  # Uses pin.orientation
       opposite_orientation = (world_orientation + 180) % 360
       
       # Direct mapping (NO Y-axis inversion here):
       if opposite_orientation < 45 or >= 315: return 0    # Right
       elif 45 <= opposite_orientation < 135: return 90   # Up  
       elif 135 <= opposite_orientation < 225: return 180 # Left
       else: return 270  # Down
   ```

### **Our Implementation vs Circuit-Synth**

#### **Key Differences Found:**

1. **Y-Coordinate Negation** ⭐ **CRITICAL**:
   - **Circuit-Synth**: Uses `-pin.position.y` in transformations
   - **Our Code**: Uses `pin.position.y` directly
   - **Impact**: Pin positions are flipped vertically

2. **Pin Attribute Names**:
   - **Circuit-Synth**: Uses `pin.orientation` (int)
   - **Our Code**: Uses `pin.rotation` (float)
   - **Status**: Values appear to be the same

3. **Transformation Logic**:
   - **Circuit-Synth**: Custom transform with Y-negation
   - **Our Code**: Standard geometric transformation
   - **Impact**: Different pin position results

4. **Label Orientation Mapping**:
   - **Circuit-Synth**: Direct 1:1 mapping (90° = Up, 270° = Down)
   - **Our Code**: Attempted Y-axis compensation (90° → 270°, 270° → 90°)
   - **Issue**: Our compensation was wrong because base transformation is different

### **Root Cause Analysis**

The **fundamental issue** is that circuit-synth handles the KiCAD Y-axis inversion at the **transformation level** (by negating Y coordinates), while we tried to handle it at the **orientation mapping level**.

**Circuit-synth approach**: Transform coordinates correctly → Use standard orientation mapping
**Our approach**: Use standard transformation → Try to compensate in orientation (WRONG)

### **Resistor Pin Analysis from KiCAD Symbol**

From Device.kicad_sym:
```
Pin 1: (at 0 3.81 270)   ← Pin at +3.81 Y, orientation 270° (UP)
Pin 2: (at 0 -3.81 90)   ← Pin at -3.81 Y, orientation 90° (DOWN)
```

With circuit-synth Y-negation:
- **Pin 1**: Y = 3.81 → **-3.81** (negated) → Component center + (-3.81) → **LOWER Y** (higher on schematic)
- **Pin 2**: Y = -3.81 → **3.81** (negated) → Component center + 3.81 → **HIGHER Y** (lower on schematic)

This explains why:
- **Pin 1** ends up as the **TOP pin** (user observation: Y=97.79)
- **Pin 2** ends up as the **BOTTOM pin** (user observation: Y=105.41)

## Proposed Solution

### **Phase 1: Fix Pin Position Calculation**
1. **Update `apply_transformation`** to match circuit-synth Y-negation logic
2. **Use `pin.orientation` if available**, fallback to `pin.rotation`
3. **Implement circuit-synth transformation exactly**

### **Phase 2: Fix Label Orientation**
1. **Use direct orientation mapping** (no Y-axis compensation)
2. **Follow circuit-synth mapping exactly**: 90° = Up, 270° = Down
3. **Test with real KiCAD files** to verify orientations

### **Phase 3: Comprehensive Testing**
1. **Verify pin positions** match KiCAD display exactly
2. **Test all pin orientations** (0°, 90°, 180°, 270°)
3. **Validate label readability** and electrical connectivity

## Technical Implementation

### **Critical Fix #1: Pin Position Transformation**
```python
# Fix apply_transformation to match circuit-synth
def apply_transformation(point: Tuple[float, float], origin: Point, rotation: float, mirror: Optional[str] = None) -> Tuple[float, float]:
    x, y = point
    
    # CIRCUIT-SYNTH APPROACH: Negate Y for KiCAD coordinate system
    y = -y  # This is the missing piece!
    
    # Apply rotation (standard)
    if rotation == 90: x, y = -y, x
    elif rotation == 180: x, y = -x, -y  
    elif rotation == 270: x, y = y, -x
    
    return (origin.x + x, origin.y + y)
```

### **Critical Fix #2: Label Orientation Mapping**
```python
# Use direct mapping (no Y-axis compensation)
def calculate_label_orientation(pin_orientation: float, component_rotation: float) -> float:
    world_orientation = (pin_orientation + component_rotation) % 360
    opposite_orientation = (world_orientation + 180) % 360
    
    # Direct circuit-synth mapping:
    if opposite_orientation < 45 or >= 315: return 0    # Right
    elif 45 <= opposite_orientation < 135: return 90   # Up
    elif 135 <= opposite_orientation < 225: return 180 # Left  
    else: return 270  # Down
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
1. ✅ **Implement circuit-synth Y-negation transformation logic**
2. ✅ **Use direct orientation mapping (no double-compensation)**
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

### **Phase 1: Fix Coordinate Transformation (Estimated: 2 hours)**
1. **Update `apply_transformation`** to match circuit-synth Y-negation
2. **Update `get_component_pin_position`** to use corrected transformation
3. **Test pin positions** against KiCAD manual measurements
4. **Verify all components** have correct pin locations

### **Phase 2: Fix Label Orientation (Estimated: 1 hour)**
1. **Remove Y-axis compensation** from orientation mapping
2. **Use direct circuit-synth mapping** (90° = Up, 270° = Down)
3. **Test label orientations** with manual KiCAD verification
4. **Ensure all labels** are readable and point away from pins

### **Phase 3: Integration and Testing (Estimated: 2 hours)**
1. **Update MCP server** with corrected logic
2. **Run comprehensive tests** to verify all functionality
3. **Create voltage divider** with proper electrical connectivity
4. **Validate with real KiCAD projects**

## Migration Impact

### **Repositories Affected:**
1. **kicad-sch-api**: Gets corrected pin positioning and label logic (🔧 **Fixed**)
2. **mcp-kicad-sch-api**: Gets working MCP tools using corrected logic (⬆️ Enhanced)  
3. **circuit-synth**: Remains unchanged (already working correctly)

### **Benefits:**
- **Correct Pin Positioning**: Pin positions match KiCAD exactly
- **Proper Label Orientation**: Labels are readable and correctly oriented
- **Electrical Connectivity**: Generated schematics have working connections
- **Circuit-Synth Compatibility**: Same algorithms for consistent results

---

**Total Estimated Time**: 5 hours (reduced due to specific fixes identified)  
**Priority**: **CRITICAL** (Blocking usable schematic generation)  
**Root Cause**: **Y-coordinate negation missing in transformation logic**
**Fix**: **Apply circuit-synth Y-negation transformation exactly**

## Next Steps

1. **Immediate**: Fix `apply_transformation` with Y-negation
2. **Verify**: Pin positions match KiCAD coordinates exactly  
3. **Fix**: Label orientation mapping to use direct circuit-synth approach
4. **Test**: Complete voltage divider with proper connectivity
5. **Integrate**: Update MCP server with working logic