# Fork Implementation Checklist

## Date: 2025-11-02
## Goal: Add REST panel support to trelliscopejs-lib for Python package

---

## Prerequisites

- [x] Codebase analysis complete
- [x] Modification points identified
- [x] Code patches created
- [ ] Fork repository on GitHub
- [ ] Clone fork locally

---

## Phase 1: Code Modifications (Est: 2-4 hours)

### Step 1.1: Fork and Setup
- [ ] Fork https://github.com/hafen/trelliscopejs-lib to your GitHub account
- [ ] Clone fork: `git clone https://github.com/YOUR-USERNAME/trelliscopejs-lib.git`
- [ ] Create branch: `git checkout -b feature/python-rest-panels`
- [ ] Install dependencies: `npm install`
- [ ] Verify build works: `npm run build`

### Step 1.2: Apply Type Definition Changes

**File:** `src/types/configs.d.ts`

Changes:
- [ ] Line ~410: Add `IFilePanelSource` interface
- [ ] Line ~420: Change `IPanelMeta.source` from `IJSPanelSource` to union type
- [ ] Add type guard helper functions (optional but recommended)

**Verification:**
```bash
# Check TypeScript compilation
npm run build
# Should compile without errors
```

**Detailed Changes:**

Location 1 - Add IFilePanelSource (after line 407):
```typescript
interface IFilePanelSource extends IPanelSource {
  type: 'file';
}
```

Location 2 - Update IPanelMeta.source (line ~420):
```typescript
interface IPanelMeta extends IMeta {
  paneltype: PanelType;
  aspect: number;
  source: IJSPanelSource | IRESTPanelSource | IFilePanelSource;  // CHANGED
}
```

Location 3 - Add type guards (optional, after IPanelMeta):
```typescript
export function isRESTPanel(source: IPanelMeta['source']): source is IRESTPanelSource {
  return source.type === 'REST';
}

export function isJSPanel(source: IPanelMeta['source']): source is IJSPanelSource {
  return source.type === 'JS';
}

export function isFilePanel(source: IPanelMeta['source']): source is IFilePanelSource {
  return source.type === 'file';
}
```

### Step 1.3: Update PanelGraphicWrapper Component

**File:** `src/components/Panel/PanelGraphicWrapper.tsx`

Changes:
- [ ] Extract panel source URL logic into `getPanelSrc()` function
- [ ] Add REST panel URL construction
- [ ] Update component to use new function

**Option A: Apply Patch**
```bash
cd /path/to/trelliscopejs-lib
patch -p1 < /path/to/PanelGraphicWrapper.tsx.patch
```

**Option B: Manual Edit**

Replace lines 44-52 (the src prop in return statement) with:
```typescript
  /**
   * Build panel source URL based on source type
   * MODIFIED for Python package REST panel support
   */
  const getPanelSrc = (): string | React.ReactElement => {
    // JavaScript-based panels (existing functionality)
    if (meta?.source?.type === 'JS' && meta?.source?.function) {
      return panelSrc;
    }

    // REST API panels (NEW - Python package support)
    if (meta?.source?.type === 'REST') {
      const restSource = meta.source as IRESTPanelSource;
      return `${restSource.url}/${fileName}`;
    }

    // Non-local panels (URL provided directly)
    if (meta?.source?.isLocal === false) {
      return fileName.toString();
    }

    // Local file panels (default - existing functionality)
    return panelSrcGetter(basePath, fileName as string, snakeCase(displayName)).toString();
  };

  return (
    <PanelGraphic
      type={meta?.paneltype}
      src={getPanelSrc()}  // CHANGED: Use function instead of inline logic
      alt={alt}
      // ... rest of props unchanged
```

**Verification:**
```bash
npm run build
# Check for TypeScript errors
# Should see: "built successfully"
```

### Step 1.4: Test Compilation

- [ ] Run `npm run build`
- [ ] Check `dist/` directory created
- [ ] No TypeScript errors
- [ ] No lint errors (run `npm run lint` if available)

**Expected Output:**
```
vite v5.x.x building for production...
✓ xxx modules transformed.
dist/assets/index-xxxxx.js
dist/assets/index-xxxxx.css
✓ built in Xs
```

---

## Phase 2: Integration Testing (Est: 2-3 hours)

### Step 2.1: Bundle with Python Package

- [ ] Copy built viewer to Python package
  ```bash
  # From fork directory
  npm run build

  # Copy to Python package
  cp -r dist/* /path/to/py-trelliscope2/trelliscope/viewer/
  ```

### Step 2.2: Test with Panel Server

**Terminal 1: Start Panel Server**
```bash
cd /path/to/py-trelliscope2/examples
python3 panel_server.py
```

**Terminal 2: Open Viewer**
```bash
# Navigate to http://localhost:5001/minimal_viewer.html
# OR use the built viewer at http://localhost:5001/
```

**Test Checklist:**
- [ ] Viewer loads without JavaScript errors
- [ ] REST panels load and display
- [ ] Panel images visible (not "No Image")
- [ ] Panel metadata displays correctly
- [ ] No CORS errors in console
- [ ] Server logs show successful panel requests

**Success Criteria:**
```
✓ 3 panels visible
✓ Panel metadata shown (id, value, category)
✓ No "No Image" placeholders
✓ Server logs: "GET /api/panels/minimal_manual/0" 200
```

### Step 2.3: Browser DevTools Verification

**Open Browser DevTools (F12):**

**Console Tab:**
- [ ] No errors
- [ ] See logs: "Panel loaded: http://localhost:5001/api/panels/..."

**Network Tab:**
- [ ] Filter: XHR/Fetch
- [ ] See successful requests to `/api/panels/minimal_manual/0`, `/1`, `/2`
- [ ] All return 200 OK
- [ ] Content-Type: image/png

**Elements Tab:**
- [ ] Inspect panel cards
- [ ] See `<img src="http://localhost:5001/api/panels/minimal_manual/0" ...>`
- [ ] Images loaded (naturalWidth > 0)

---

## Phase 3: Commit and Push (Est: 1 hour)

### Step 3.1: Review Changes

```bash
git status
git diff src/types/configs.d.ts
git diff src/components/Panel/PanelGraphicWrapper.tsx
```

**Verify Changes:**
- [ ] Only modified files are type definitions and PanelGraphicWrapper
- [ ] No unintended changes
- [ ] No debugging code left in

### Step 3.2: Commit

```bash
git add src/types/configs.d.ts
git add src/components/Panel/PanelGraphicWrapper.tsx
git commit -m "Add REST panel support for Python package integration

- Update IPanelMeta to accept REST panel sources
- Add REST URL construction in PanelGraphicWrapper
- Support file-based panel sources
- Add type guard functions for panel source types

This enables trelliscopejs-lib to render panels served via REST API,
allowing integration with the py-trelliscope2 Python package.

Refs: py-trelliscope2 issue #XXX"
```

### Step 3.3: Push to Fork

```bash
git push origin feature/python-rest-panels
```

- [ ] Pushed successfully
- [ ] Verify on GitHub: https://github.com/YOUR-USERNAME/trelliscopejs-lib/tree/feature/python-rest-panels

---

## Phase 4: Python Package Integration (Est: 2-3 hours)

### Step 4.1: Update Python Package to Use Fork

**File:** `py-trelliscope2/trelliscope/writers/json_writer.py`

Add method to create REST panel metadata:
```python
def _create_rest_panel_meta(self, display: Display) -> dict:
    """Create REST panel metadata for displayInfo.json"""
    return {
        "varname": display.panel_col,
        "type": "panel",
        "label": "Panel",
        "paneltype": "img",
        "aspect": display.aspect_ratio or 1.0,
        "source": {
            "type": "REST",
            "url": display.panel_interface.base,
            "isLocal": False,
            "port": display.panel_interface.port or 5001
        },
        "tags": ["panel"],
        "filterable": False,
        "sortable": False
    }
```

Update `write_display_info()`:
```python
def write_display_info(self, display: Display, output_dir: Path):
    # ... existing code ...

    metas = []

    # Add panel meta
    if display.panel_interface.type == "REST":
        metas.append(self._create_rest_panel_meta(display))

    # Add other metas
    # ... existing code ...
```

### Step 4.2: Bundle Forked Viewer

**Create bundling script:** `scripts/bundle_viewer.sh`
```bash
#!/bin/bash
# Bundle forked trelliscopejs-lib viewer with Python package

FORK_DIR="/path/to/trelliscopejs-lib"
PACKAGE_DIR="/path/to/py-trelliscope2"

echo "Building viewer..."
cd $FORK_DIR
npm run build

echo "Copying to Python package..."
mkdir -p $PACKAGE_DIR/trelliscope/viewer/assets
cp dist/index.html $PACKAGE_DIR/trelliscope/viewer/
cp -r dist/assets/* $PACKAGE_DIR/trelliscope/viewer/assets/

echo "✓ Viewer bundled successfully"
```

- [ ] Make executable: `chmod +x scripts/bundle_viewer.sh`
- [ ] Run: `./scripts/bundle_viewer.sh`
- [ ] Verify files copied

### Step 4.3: Update Writer to Copy Viewer

**File:** `trelliscope/writers/json_writer.py`

```python
def copy_viewer_files(self, output_dir: Path):
    """Copy bundled viewer to output directory"""
    viewer_src = Path(__file__).parent.parent / 'viewer'

    # Copy index.html
    shutil.copy(viewer_src / 'index.html', output_dir / 'index.html')

    # Copy assets
    assets_dst = output_dir / 'assets'
    if assets_dst.exists():
        shutil.rmtree(assets_dst)
    shutil.copytree(viewer_src / 'assets', assets_dst)
```

### Step 4.4: End-to-End Test

**Test Script:** `examples/test_fork_integration.py`
```python
import pandas as pd
from trelliscope import Display

# Create test data
data = pd.DataFrame({
    'id': [0, 1, 2],
    'value': [0, 10, 20],
    'panel': ['0', '1', '2']
})

# Create display with REST panels
display = Display(data, name='fork_test')
display.set_panel_column('panel')
display.set_panel_interface(
    type='REST',
    base='http://localhost:5001/api/panels/fork_test'
)

# Write
display.write('./output')

print("✓ Display created")
print("✓ Open http://localhost:5001/ to view")
```

**Run Test:**
```bash
# Terminal 1: Start panel server
cd examples
python3 panel_server.py

# Terminal 2: Run test
python3 test_fork_integration.py

# Terminal 3: Open browser
open http://localhost:5001/
```

**Verification:**
- [ ] Display appears in viewer
- [ ] Panels load via REST API
- [ ] All 3 panels visible
- [ ] No errors in browser console

---

## Phase 5: Documentation (Est: 2 hours)

### Step 5.1: Update Fork README

**Create:** `README_PYTHON_FORK.md` in fork repo

```markdown
# Trelliscope Viewer - Python Fork

This fork adds REST panel support for the [py-trelliscope2](https://github.com/YOUR-ORG/py-trelliscope2) Python package.

## Changes from Upstream

### New Features
- REST API panel support
- File-based panel support
- Extended type definitions for panel sources

### Modified Files
- `src/types/configs.d.ts` - Type definitions
- `src/components/Panel/PanelGraphicWrapper.tsx` - Panel URL construction

### Code Additions
~50 lines of new code for REST panel loading.

## Building

```bash
npm install
npm run build
```

Output: `dist/` directory

## Integration with Python

This viewer is bundled with py-trelliscope2:

```python
from trelliscope import Display

display = Display(data)
display.set_panel_interface(type='REST', base='http://localhost:5001/api/panels/my_display')
display.write()
```

## Maintenance

Track upstream:
```bash
git fetch upstream
git merge upstream/main
```

## License

MIT (same as upstream)
```

- [ ] Add to fork repository
- [ ] Commit and push

### Step 5.2: Update Python Package Docs

**File:** `py-trelliscope2/README.md`

Add section on panel rendering:
```markdown
## Panel Rendering

py-trelliscope2 uses a custom fork of trelliscopejs-lib with REST panel support.

### REST API Panels (Recommended)

```python
from trelliscope import Display, start_panel_server

display = Display(data)
display.set_panel_interface(type='REST', base='http://localhost:5001/api/panels/my_display')
display.write('./output')

start_panel_server('./output', port=5001)
```

### File-based Panels

```python
display.set_panel_interface(type='file', extension='png')
```

See [fork repository](https://github.com/YOUR-ORG/trelliscopejs-lib) for viewer details.
```

- [ ] Update Python package README
- [ ] Commit changes

---

## Phase 6: Release (Est: 1 hour)

### Step 6.1: Tag Fork Version

```bash
cd /path/to/trelliscopejs-lib
git tag v0.7.14-python.1
git push origin v0.7.14-python.1
```

**Version scheme:** `<upstream-version>-python.<fork-version>`

### Step 6.2: Create GitHub Release

- [ ] Go to fork repository on GitHub
- [ ] Click "Releases" → "Create a new release"
- [ ] Tag: `v0.7.14-python.1`
- [ ] Title: "Python Package Support v0.7.14-python.1"
- [ ] Description:
  ```markdown
  ## Python Package Support Release

  This fork adds REST panel rendering support for the py-trelliscope2 Python package.

  ### Changes
  - ✅ REST API panel support
  - ✅ File-based panel support
  - ✅ Extended type definitions

  ### Files Changed
  - `src/types/configs.d.ts`
  - `src/components/Panel/PanelGraphicWrapper.tsx`

  ### Integration
  Bundled with [py-trelliscope2](https://github.com/YOUR-ORG/py-trelliscope2)

  ### Build
  ```bash
  npm install
  npm run build
  ```

  Output available in `dist/` directory.
  ```
- [ ] Attach built assets (optional)
- [ ] Publish release

### Step 6.3: Update Python Package to Use Fork

**File:** `py-trelliscope2/setup.py` or `pyproject.toml`

Update metadata to reference fork:
```python
# setup.py
setup(
    # ... existing config ...
    package_data={
        'trelliscope': [
            'viewer/**/*',
            'viewer/assets/**/*'
        ]
    },
    project_urls={
        'Viewer Fork': 'https://github.com/YOUR-ORG/trelliscopejs-lib',
        # ... other URLs
    }
)
```

- [ ] Update setup configuration
- [ ] Test package installation
- [ ] Verify viewer files included

---

## Final Verification Checklist

### Fork Repository
- [ ] Code changes committed
- [ ] Tagged with version
- [ ] GitHub release created
- [ ] README updated
- [ ] All tests passing (if added)

### Python Package
- [ ] Viewer bundled correctly
- [ ] REST panel metadata generated correctly
- [ ] Integration test passing
- [ ] Documentation updated
- [ ] Example working

### End-to-End Test
- [ ] Create display with Python
- [ ] Start panel server
- [ ] Open viewer in browser
- [ ] Panels load via REST API
- [ ] No console errors
- [ ] Panel metadata displays
- [ ] All interactions work (zoom, filter, etc.)

---

## Success Metrics

- [x] Codebase analyzed
- [x] Modification points identified
- [x] Code patches created
- [ ] Fork created and modified
- [ ] Build successful
- [ ] Integration test passing
- [ ] Documentation complete
- [ ] Release tagged
- [ ] Python package integrated
- [ ] End-to-end test passing

---

## Troubleshooting

### Build Errors

**TypeScript Error: "Type 'IRESTPanelSource' is not assignable to type 'IJSPanelSource'"**
- Check that `IPanelMeta.source` uses union type
- Verify all interfaces defined

**"Module not found" errors**
- Run `npm install` again
- Delete `node_modules/` and reinstall

### Runtime Errors

**"No Image" placeholders in viewer**
- Check server logs for panel requests
- Verify REST URL construction in browser DevTools
- Check CORS headers

**CORS errors**
- Ensure panel_server.py has CORS enabled
- Check response headers in Network tab

**Panels not loading**
- Check `meta.source.type === 'REST'` in displayInfo.json
- Verify `meta.source.url` is correct base URL
- Check `fileName` prop contains panel ID

---

## Time Estimates

| Phase | Estimated Time | Actual Time |
|-------|---------------|-------------|
| Code Modifications | 2-4 hours | _____ |
| Integration Testing | 2-3 hours | _____ |
| Commit and Push | 1 hour | _____ |
| Python Integration | 2-3 hours | _____ |
| Documentation | 2 hours | _____ |
| Release | 1 hour | _____ |
| **Total** | **10-15 hours** | **_____** |

---

**Checklist created:** 2025-11-02
**Ready to implement:** Yes
**Next step:** Fork repository and begin Phase 1
