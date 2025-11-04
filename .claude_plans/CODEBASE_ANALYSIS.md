# Trelliscope Viewer Codebase Analysis

## Date: 2025-11-02
## Repository: https://github.com/hafen/trelliscopejs-lib
## Version Analyzed: v0.7.14 (latest available)
## Clone Location: `/Users/matthewdeane/Documents/Data Science/python/_projects/viewer_fork/trelliscopejs-lib`

---

## Executive Summary

**Finding:** The viewer ALREADY has type definitions for REST panels (`PanelSourceType` includes `'REST'`), but the implementation is missing in the panel rendering logic.

**Root Cause:** The `PanelGraphicWrapper` component builds the `src` URL for panels but doesn't handle the REST API case. It only handles:
- JavaScript-based panels (`meta.source.type === 'JS'`)
- Local file panels (via `panelSrcGetter`)

**Solution:** Add REST panel handling to `PanelGraphicWrapper.tsx` to construct REST API URLs when `meta.source.type === 'REST'`.

---

## Architecture Overview

### Technology Stack
- **Framework:** React 18+ with TypeScript
- **State Management:** Redux Toolkit with RTK Query
- **Build Tool:** Vite
- **UI Library:** Material-UI (MUI)
- **Package Manager:** npm

### Directory Structure
```
src/
├── components/
│   └── Panel/
│       ├── Panel.tsx                  # Main panel container component
│       ├── PanelGraphic.tsx           # Panel rendering component (handles img, iframe, HTML)
│       ├── PanelGraphicWrapper.tsx    # **KEY FILE** - Determines panel source URL
│       └── Panel.module.scss
├── slices/
│   ├── displayInfoAPI.ts              # Loads displayInfo.json via RTK Query
│   └── ...
├── types/
│   ├── configs.d.ts                   # Type definitions for DisplayInfo
│   └── ...
└── utils.ts                           # Utility functions including panelSrcGetter
```

---

## Data Flow

### 1. Display Configuration Loading

```
User opens viewer
    ↓
displayInfoAPI.ts loads displayInfo.json
    ↓
Redux store populated with IDisplay data
    ↓
Components access via useDisplayInfo()
```

**File:** `src/slices/displayInfoAPI.ts`
- Fetches `displayInfo.json` from `{basePath}/displays/{displayName}/displayInfo.json`
- Parses panel metadata from `displayInfo.metas` array
- Provides hooks: `useDisplayInfo()`, `useDisplayMetas()`, `useMetaByVarname()`

### 2. Panel Rendering Flow

```
Content component renders grid
    ↓
For each row: Extracts panel metadata (IPanelMeta)
    ↓
Panel.tsx (container)
    ↓
PanelGraphicWrapper.tsx (determines src URL)  ← **MODIFICATION NEEDED**
    ↓
PanelGraphic.tsx (renders based on type)
```

**Panel.tsx** (src/components/Panel/Panel.tsx:69)
- Container component
- Renders children (which is PanelGraphic)
- Handles expand button, labels, panel picker

**PanelGraphicWrapper.tsx** (src/components/Panel/PanelGraphicWrapper.tsx:44-63)
- **CRITICAL FILE** - This is where we need to add REST support
- Determines the `src` URL based on `meta.source.type`
- Currently handles:
  - `meta.source.type === 'JS'` - JavaScript function-based panels
  - `meta.source.isLocal === false` - Direct URL (returns fileName as-is)
  - Default - Local files via `panelSrcGetter()`

**PanelGraphic.tsx** (src/components/Panel/PanelGraphic.tsx:19-161)
- Renders the actual panel based on `type` prop:
  - `type === 'img'` - Image via `<img>` tag
  - `type === 'iframe'` - Iframe via `<iframe>`
  - `type === 'iframeSrcDoc'` - Iframe with srcDoc
  - `type === 'htmlContent'` - HTML content
- Handles loading states, errors, WebSocket loading

---

## Type Definitions

### Panel Source Types (src/types/configs.d.ts:403)

```typescript
type PanelSourceType = 'file' | 'REST' | 'localWebSocket' | 'JS';
```

**Note:** `'REST'` is already defined in types! Just not implemented.

### Panel Types (src/types/configs.d.ts:401)

```typescript
type PanelType = 'img' | 'iframe' | 'iframeSrcDoc' | 'htmlContent';
```

### Panel Source Interfaces (src/types/configs.d.ts:410-426)

```typescript
interface IPanelSource {
  type: PanelSourceType;
  isLocal: boolean;
  port: number;
}

interface IJSPanelSource extends IPanelSource {
  function?: PanelFunction;
}

interface IRESTPanelSource extends IPanelSource {
  url: string;
  apiKey: string | undefined;
  headers: string | undefined;
}
```

**Note:** `IRESTPanelSource` exists but `IPanelMeta.source` is typed as `IJSPanelSource`, not a union type!

### Panel Meta (src/types/configs.d.ts:418-423)

```typescript
interface IPanelMeta extends IMeta {
  paneltype: PanelType;
  aspect: number;
  source: IJSPanelSource;  // ← PROBLEM: Should be IJSPanelSource | IRESTPanelSource
}
```

---

## Current Implementation Gaps

### Gap 1: PanelGraphicWrapper doesn't handle REST

**File:** `src/components/Panel/PanelGraphicWrapper.tsx` (lines 47-52)

**Current Code:**
```typescript
<PanelGraphic
  src={
    meta?.source?.type === 'JS' && meta?.source?.function
      ? panelSrc
      : meta?.source?.isLocal === false
        ? fileName.toString()
        : panelSrcGetter(basePath, fileName as string, snakeCase(displayName)).toString()
  }
```

**Problem:**
- If `meta.source.type === 'REST'`, it falls through to the default case
- Default case calls `panelSrcGetter()` which creates: `{basePath}/displays/{displayName}/{fileName}`
- This creates a file path, not a REST API URL

**What Should Happen:**
- Check if `meta.source.type === 'REST'`
- If so, build REST URL from `meta.source.url` (or base) and panel ID
- Something like: `{meta.source.url}/{panelId}`

### Gap 2: Type Definition Mismatch

**File:** `src/types/configs.d.ts` (line 420)

**Problem:**
```typescript
interface IPanelMeta extends IMeta {
  source: IJSPanelSource;  // Too restrictive
}
```

**Should be:**
```typescript
interface IPanelMeta extends IMeta {
  source: IJSPanelSource | IRESTPanelSource | IFilePanelSource;
}
```

This allows TypeScript to accept REST panel sources.

### Gap 3: No REST Panel Data Mapping

**Issue:** The displayInfo.json from Python package uses this structure:
```json
{
  "panelInterface": {
    "type": "REST",
    "base": "http://localhost:5001/api/panels/minimal_manual",
    "panelCol": "panel"
  }
}
```

But `IPanelMeta.source` expects:
```typescript
{
  type: "REST",
  url: "...",
  isLocal: false,
  port: 5001
}
```

**Need to understand:** Where is `panelInterface` converted to `meta.source`? Is this happening?

---

## Exact Modification Points

### Modification 1: Update PanelGraphicWrapper.tsx

**File:** `src/components/Panel/PanelGraphicWrapper.tsx`
**Lines:** 44-63 (the return statement)

**Change Type:** Add REST panel URL construction

**Before:**
```typescript
<PanelGraphic
  src={
    meta?.source?.type === 'JS' && meta?.source?.function
      ? panelSrc
      : meta?.source?.isLocal === false
        ? fileName.toString()
        : panelSrcGetter(basePath, fileName as string, snakeCase(displayName)).toString()
  }
```

**After:**
```typescript
<PanelGraphic
  src={
    meta?.source?.type === 'JS' && meta?.source?.function
      ? panelSrc
      : meta?.source?.type === 'REST'
        ? `${(meta.source as IRESTPanelSource).url}/${fileName}`  // NEW: REST panel URL
        : meta?.source?.isLocal === false
          ? fileName.toString()
          : panelSrcGetter(basePath, fileName as string, snakeCase(displayName)).toString()
  }
```

**Estimated Lines:** 3-5 lines changed

### Modification 2: Update Type Definitions

**File:** `src/types/configs.d.ts`
**Line:** 420 (IPanelMeta.source)

**Change Type:** Widen type to accept REST panels

**Before:**
```typescript
interface IPanelMeta extends IMeta {
  paneltype: PanelType;
  aspect: number;
  source: IJSPanelSource;
}
```

**After:**
```typescript
interface IPanelMeta extends IMeta {
  paneltype: PanelType;
  aspect: number;
  source: IJSPanelSource | IRESTPanelSource | IFilePanelSource;
}
```

**Also Needed:** Define `IFilePanelSource` if not exists:
```typescript
interface IFilePanelSource extends IPanelSource {
  type: 'file';
}
```

**Estimated Lines:** 5-10 lines changed

### Modification 3: Handle PanelInterface → Meta.Source Mapping

**Investigation Needed:** Find where `displayInfo.panelInterface` is converted to individual panel `meta.source` objects.

**Likely Location:** Somewhere in data processing or Redux slices

**Search for:**
```bash
grep -r "panelInterface" src/slices src/reducers --include="*.ts"
```

**Expected Mapping:**
```typescript
// When loading displayInfo
const panelInterface = displayInfo.panelInterface;

// For each panel meta where type === 'panel'
panelMeta.source = {
  type: panelInterface.type,
  url: panelInterface.base,  // Map 'base' to 'url'
  isLocal: panelInterface.type !== 'REST',
  port: extractPortFromURL(panelInterface.base)
};
```

**Estimated Lines:** 10-20 lines new code

---

## Implementation Strategy

### Phase 1: Minimal REST Support (Hours 1-4)

**Goal:** Get REST panels rendering with minimal changes

**Tasks:**
1. ✓ Understand current architecture (DONE)
2. Modify `PanelGraphicWrapper.tsx` to handle REST source
3. Update `IPanelMeta` type definition
4. Test with existing Python-generated displayInfo.json

**Files to Modify:**
- `src/components/Panel/PanelGraphicWrapper.tsx` (5 lines)
- `src/types/configs.d.ts` (10 lines)

**Testing:**
1. Build viewer: `npm run build`
2. Copy dist/ to Python package
3. Test with panel_server.py REST API
4. Verify panels load in browser

### Phase 2: Complete REST Integration (Hours 5-12)

**Goal:** Handle all REST edge cases and panelInterface mapping

**Tasks:**
1. Find panelInterface → meta.source mapping location
2. Add conversion logic for REST panel metadata
3. Handle authentication headers (if needed)
4. Add error handling for failed REST requests
5. Update PanelGraphic to show better loading states

**Files to Modify:**
- Data mapping logic (TBD - need to find file)
- `src/components/Panel/PanelGraphic.tsx` (improve loading/error UI)
- Add unit tests

### Phase 3: File Panel Support (Hours 13-16)

**Goal:** Bonus feature - support file-based panels too

**Tasks:**
1. Add `IFilePanelSource` type
2. Update PanelGraphicWrapper for file panels
3. Test with file-based displayInfo.json

**Files to Modify:**
- Same as Phase 1 but with file handling

### Phase 4: Testing & Documentation (Hours 17-20)

**Goal:** Comprehensive testing and documentation

**Tasks:**
1. Unit tests for new panel loading logic
2. Integration tests with Python package
3. Browser tests (Playwright)
4. Update README and documentation

---

## Panel Source Type Comparison

| Source Type | Current Support | After Fork | URL Construction |
|-------------|----------------|------------|------------------|
| `'JS'` | ✅ Yes | ✅ Yes | JavaScript function result |
| `'localWebSocket'` | ✅ Yes | ✅ Yes | WebSocket connection |
| `'file'` | ⚠️ Partial | ✅ Yes | `panelSrcGetter()` - local path |
| `'REST'` | ❌ **NO** | ✅ **YES** | `{base}/{panelId}` |

---

## Risk Assessment

### Low Risk Changes
- ✅ Updating type definitions (non-breaking)
- ✅ Adding REST URL construction (isolated change)
- ✅ All changes are additive, not replacing existing code

### Medium Risk Changes
- ⚠️ PanelInterface → Meta.Source mapping (if needed)
- ⚠️ Handling authentication headers
- ⚠️ CORS handling (already handled by server)

### Testing Checklist
- [ ] REST panels load successfully
- [ ] Existing htmlwidget panels still work
- [ ] JS panels still work
- [ ] File panels still work
- [ ] Error states display correctly
- [ ] Loading states display correctly
- [ ] No TypeScript errors
- [ ] No console errors in browser

---

## Code Dependencies

### Key Utility Functions

**panelSrcGetter** (src/utils.ts:42-43)
```typescript
export const panelSrcGetter = (basePath: string, fileName: string, displayName: string) =>
  `${basePath}/displays/${displayName}/${fileName}`;
```
- Used for constructing local file panel URLs
- Returns: `{basePath}/displays/{snake_case_display_name}/{fileName}`
- Example: `/displays/minimal_manual/panels/0.png`

**snakeCase** (src/utils.ts:21)
```typescript
export const snakeCase = (str: string) => str.replace(/([^a-zA-Z0-9_])/g, '_');
```
- Converts display names to snake_case
- Example: `"My Display"` → `"My_Display"`

### Key Hooks

**useDisplayInfo** (src/slices/displayInfoAPI.ts:82-92)
```typescript
export const useDisplayInfo = () => {
  // Returns RTK Query result with displayInfo data
  // Usage: const { data: displayInfo } = useDisplayInfo();
}
```

**useDisplayMetas** (src/slices/displayInfoAPI.ts:105-108)
```typescript
export const useDisplayMetas = () => {
  // Returns array of IMeta objects from displayInfo
  // Includes panel metadata (where meta.type === 'panel')
}
```

---

## Python Package Integration Points

### DisplayInfo.json Format (Python generates this)

**Current Python Output:**
```json
{
  "name": "minimal_manual",
  "description": "Minimal manual display",
  "metas": [
    {
      "varname": "panel",
      "type": "panel",
      "paneltype": "img",
      "aspect": 1,
      "source": {
        "type": "REST",
        "url": "http://localhost:5001/api/panels/minimal_manual",
        "isLocal": false,
        "port": 5001
      }
    },
    {
      "varname": "id",
      "type": "number",
      "label": "ID"
    }
  ],
  "cogData": [
    {"id": 0, "panel": "0", "value": 0},
    {"id": 1, "panel": "1", "value": 10},
    {"id": 2, "panel": "2", "value": 20}
  ]
}
```

**Key Points:**
- Each panel row has a `panel` field with the panel ID
- The `panel` meta has `source.type = "REST"`
- The `source.url` is the base REST endpoint
- The viewer should construct: `{source.url}/{cogData[i].panel}`
- Result: `http://localhost:5001/api/panels/minimal_manual/0`

### Python Package Changes Needed

**File:** `trelliscope/writers/json_writer.py`

**Add method to generate REST panel metadata:**
```python
def _create_rest_panel_source(self, base_url: str, port: int = 5001) -> dict:
    """Create REST panel source metadata"""
    return {
        "type": "REST",
        "url": base_url,
        "isLocal": False,
        "port": port
    }

def write_display_info(self, display):
    # ... existing code ...

    # If display has REST panel interface:
    if display.panel_interface.type == "REST":
        panel_meta = {
            "varname": display.panel_col,
            "type": "panel",
            "paneltype": "img",
            "aspect": display.aspect_ratio or 1,
            "source": self._create_rest_panel_source(
                display.panel_interface.base,
                display.panel_interface.port
            )
        }
```

---

## Next Steps

### Immediate (This Session)
1. ✅ Complete codebase analysis (DONE)
2. ⬜ Create code patches for modifications
3. ⬜ Test build locally
4. ⬜ Verify with Python package

### Short Term (Days 1-3)
1. Fork repository on GitHub
2. Create feature branch
3. Implement Phase 1 changes
4. Test with panel_server.py
5. Commit and push

### Medium Term (Week 1)
1. Complete Phase 2 implementation
2. Add Phase 3 (file panels)
3. Write tests
4. Update documentation

### Long Term (Weeks 2-4)
1. Bundle with Python package
2. Complete integration testing
3. Release fork version
4. Consider PR to upstream (if appropriate)

---

## Questions Requiring Further Investigation

1. **Where is panelInterface converted to individual panel meta.source objects?**
   - Need to search for this mapping logic
   - Might be in displayInfoAPI or a reducer
   - Could be that Python package needs to output the right format

2. **How are panel IDs extracted from cogData?**
   - Need to see how `fileName` prop is determined
   - Likely comes from `data[meta.varname]`
   - Should be the panel ID from cogData row

3. **Is authentication needed for REST panels?**
   - IRESTPanelSource has `apiKey` and `headers` fields
   - Do we need to implement these?
   - Can defer to Phase 2

4. **Should we also support WebSocket panels?**
   - WebSocket loading code exists in PanelGraphic
   - Should we add WebSocket to Python package too?
   - Lower priority than REST

---

## Success Criteria

### Minimum Viable Fork
- ✅ REST panels load and display
- ✅ Existing panels (JS, htmlwidget) still work
- ✅ No TypeScript compilation errors
- ✅ No runtime JavaScript errors
- ✅ Works with Python package panel_server.py

### Complete Fork
- ✅ All above criteria
- ✅ File-based panels also work
- ✅ Comprehensive error handling
- ✅ Unit tests passing
- ✅ Integration tests passing
- ✅ Documentation updated
- ✅ Bundled with Python package

---

**Analysis completed:** 2025-11-02
**Estimated implementation time:** 20-30 hours
**Complexity:** Medium (clear modification points, isolated changes)
**Confidence:** High (POC proves concept works)
