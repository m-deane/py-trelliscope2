# Trelliscope Viewer Fork - Implementation Guide

## Date: 2025-11-02
## Decision: Fork trelliscopejs-lib for Python panel support
## Timeline: 3-4 weeks to production

---

## Phase 1: Repository Setup (Days 1-2)

### Step 1.1: Fork on GitHub

1. **Navigate to original repository:**
   ```
   https://github.com/hafen/trelliscopejs-lib
   ```

2. **Click "Fork" button** (top right)
   - Create fork under your organization/account
   - Suggested name: `trelliscopejs-lib` (keep same name)
   - Description: "Fork with Python panel rendering support"

3. **Clone your fork locally:**
   ```bash
   cd ~/projects
   git clone https://github.com/YOUR-USERNAME/trelliscopejs-lib.git
   cd trelliscopejs-lib
   ```

4. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/hafen/trelliscopejs-lib.git
   git fetch upstream
   ```

5. **Create feature branch:**
   ```bash
   git checkout -b feature/python-panel-support
   ```

### Step 1.2: Development Environment Setup

1. **Check Node.js version:**
   ```bash
   node --version  # Should be v16+
   npm --version   # Should be v8+
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Verify build works:**
   ```bash
   npm run build
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```
   This should open viewer at http://localhost:3000 or similar

5. **Review package.json:**
   ```bash
   cat package.json
   ```
   Note:
   - Build scripts
   - Dependencies (React, Redux versions)
   - Test commands

### Step 1.3: Codebase Exploration

1. **Examine directory structure:**
   ```bash
   tree -L 2 src/
   ```

2. **Key directories to understand:**
   ```
   src/
   ├── components/     # React components (panels, grids, etc)
   ├── store/          # Redux state management
   ├── utils/          # Utility functions
   ├── hooks/          # React hooks
   └── types/          # TypeScript types (if used)
   ```

3. **Search for panel-related code:**
   ```bash
   grep -r "panel" src/ | grep -i "interface\|type\|load" | head -20
   grep -r "htmlwidget" src/
   grep -r "cogData" src/
   ```

4. **Find panel rendering component:**
   ```bash
   find src -name "*panel*" -o -name "*Panel*"
   ls -la src/components/Panel* 2>/dev/null || echo "Check other locations"
   ```

---

## Phase 2: Code Analysis (Days 3-5)

### Step 2.1: Identify Panel Loading Logic

**Task:** Find where panels are currently loaded

**Search patterns:**
```bash
# Find panel interface handling
grep -rn "panelInterface" src/

# Find image/iframe creation
grep -rn "createElement.*img\|new Image\|createElement.*iframe" src/

# Find data fetching
grep -rn "fetch\|axios\|getData" src/ | grep -i panel
```

**Expected files to examine:**
- `src/components/Panel/Panel.jsx` or similar
- `src/utils/panelLoader.js` or similar
- `src/store/panels/panelActions.js` or similar

### Step 2.2: Document Current Architecture

Create `ARCHITECTURE_NOTES.md`:

```markdown
# Current Panel Architecture

## Panel Loading Flow
1. Component mounts: Panel.jsx
2. Fetches data from: [location]
3. Checks panelInterface.type
4. Currently only handles: 'htmlwidget'
5. Renders using: [method]

## Key Functions
- loadPanel(): [location]
- renderPanel(): [location]
- fetchPanelData(): [location]

## Data Flow
[Component] → [Action] → [Reducer] → [Render]

## Missing Pieces
- No REST panel support in: [files]
- No file panel support in: [files]
```

### Step 2.3: Create Modification Plan

**File:** `MODIFICATION_PLAN.md`

```markdown
# Files to Modify

## 1. Panel Loader (Priority: HIGH)
**File:** src/utils/panelLoader.js (or equivalent)
**Changes:**
- Add loadRestPanel() function
- Add loadFilePanel() function
- Update loadPanel() switch/if logic

## 2. Panel Component (Priority: HIGH)
**File:** src/components/Panel/Panel.jsx (or equivalent)
**Changes:**
- Handle REST panel type
- Handle file panel type
- Add loading states
- Add error states

## 3. Types (Priority: MEDIUM)
**File:** src/types/panel.ts (if TypeScript)
**Changes:**
- Add REST panel interface type
- Add file panel interface type

## 4. Tests (Priority: HIGH)
**File:** tests/panelLoader.test.js (create if needed)
**Changes:**
- Add tests for REST panels
- Add tests for file panels
```

---

## Phase 3: Implementation (Days 6-12)

### Step 3.1: Create Panel Loader Utilities

**File:** `src/utils/panelLoader.js` (new or modify existing)

```javascript
/**
 * Panel Loader for Python trelliscope2
 * Adds support for REST and file-based panels
 */

/**
 * Load a panel based on its interface type
 * @param {Object} panelInterface - Panel interface configuration
 * @param {Object} panelData - Panel data including ID/path
 * @returns {Promise<HTMLElement>} - Panel element ready to render
 */
export async function loadPanel(panelInterface, panelData) {
  const { type } = panelInterface;

  switch (type) {
    case 'htmlwidget':
      return loadHtmlWidget(panelInterface, panelData);

    case 'REST':
      return loadRestPanel(panelInterface, panelData);

    case 'file':
    case 'panel_local':
      return loadFilePanel(panelInterface, panelData);

    default:
      throw new Error(`Unsupported panel type: ${type}`);
  }
}

/**
 * Load panel from REST API
 * NEW FUNCTION - This is what's missing!
 */
export async function loadRestPanel(panelInterface, panelData) {
  const { base, panelCol } = panelInterface;
  const panelId = panelData[panelCol];

  if (!panelId) {
    throw new Error(`Panel ID not found in column: ${panelCol}`);
  }

  const imageUrl = `${base}/${panelId}`;

  return new Promise((resolve, reject) => {
    const img = document.createElement('img');
    img.className = 'panel-image';

    img.onload = () => {
      console.log(`Panel loaded: ${imageUrl}`);
      resolve(img);
    };

    img.onerror = (error) => {
      console.error(`Failed to load panel: ${imageUrl}`, error);
      reject(new Error(`Failed to load panel from ${imageUrl}`));
    };

    img.src = imageUrl;
  });
}

/**
 * Load panel from file path
 * NEW FUNCTION - Bonus feature
 */
export async function loadFilePanel(panelInterface, panelData) {
  const { panelCol, extension } = panelInterface;
  let panelPath = panelData[panelCol];

  // Add extension if not present
  if (extension && !panelPath.endsWith(`.${extension}`)) {
    panelPath = `${panelPath}.${extension}`;
  }

  return new Promise((resolve, reject) => {
    const img = document.createElement('img');
    img.className = 'panel-image';

    img.onload = () => {
      console.log(`Panel loaded: ${panelPath}`);
      resolve(img);
    };

    img.onerror = (error) => {
      console.error(`Failed to load panel: ${panelPath}`, error);
      reject(new Error(`Failed to load panel from ${panelPath}`));
    };

    img.src = panelPath;
  });
}

/**
 * Existing htmlwidget loader (keep as-is)
 * This function should already exist in the codebase
 */
function loadHtmlWidget(panelInterface, panelData) {
  // Existing implementation - don't modify
  // ...
}
```

### Step 3.2: Update Panel Component

**File:** `src/components/Panel/Panel.jsx` (modify existing)

```jsx
import React, { useEffect, useState } from 'react';
import { loadPanel } from '../../utils/panelLoader';
import './Panel.css';

/**
 * Panel component with REST and file support
 * MODIFIED for Python trelliscope2
 */
export function Panel({ panelInterface, panelData, width, height }) {
  const [panelElement, setPanelElement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function loadPanelAsync() {
      setLoading(true);
      setError(null);

      try {
        const element = await loadPanel(panelInterface, panelData);

        if (mounted) {
          setPanelElement(element);
          setLoading(false);
        }
      } catch (err) {
        console.error('Panel loading error:', err);

        if (mounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    }

    loadPanelAsync();

    return () => {
      mounted = false;
    };
  }, [panelInterface, panelData]);

  // Loading state
  if (loading) {
    return (
      <div className="panel-container panel-loading" style={{ width, height }}>
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading panel...</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="panel-container panel-error" style={{ width, height }}>
        <div className="error-icon">⚠️</div>
        <div className="error-text">{error}</div>
      </div>
    );
  }

  // Render panel
  return (
    <div className="panel-container" style={{ width, height }}>
      {panelElement && (
        <div
          ref={(ref) => {
            if (ref && !ref.contains(panelElement)) {
              ref.appendChild(panelElement);
            }
          }}
          className="panel-content"
        />
      )}
    </div>
  );
}
```

### Step 3.3: Add Panel Styles

**File:** `src/components/Panel/Panel.css` (new or modify)

```css
/* Panel container */
.panel-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

/* Panel content */
.panel-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* Loading state */
.panel-loading {
  background: #f5f5f5;
  flex-direction: column;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 12px;
  font-size: 14px;
  color: #666;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error state */
.panel-error {
  background: #fff5f5;
  flex-direction: column;
}

.error-icon {
  font-size: 32px;
}

.error-text {
  margin-top: 8px;
  font-size: 13px;
  color: #d32f2f;
  text-align: center;
  padding: 0 16px;
}
```

### Step 3.4: Add TypeScript Types (if applicable)

**File:** `src/types/panel.ts` (if TypeScript is used)

```typescript
// Panel interface types
export type PanelInterfaceType = 'htmlwidget' | 'REST' | 'file' | 'panel_local';

export interface BasePanelInterface {
  type: PanelInterfaceType;
  panelCol: string;
}

export interface HtmlWidgetInterface extends BasePanelInterface {
  type: 'htmlwidget';
  deps?: any;
  // ... existing htmlwidget fields
}

// NEW: REST panel interface
export interface RestPanelInterface extends BasePanelInterface {
  type: 'REST';
  base: string;  // Base URL for REST API
}

// NEW: File panel interface
export interface FilePanelInterface extends BasePanelInterface {
  type: 'file' | 'panel_local';
  extension?: string;  // Optional file extension
}

export type PanelInterface =
  | HtmlWidgetInterface
  | RestPanelInterface
  | FilePanelInterface;
```

---

## Phase 4: Testing (Days 13-17)

### Step 4.1: Unit Tests

**File:** `tests/panelLoader.test.js` (new)

```javascript
import { loadPanel, loadRestPanel, loadFilePanel } from '../src/utils/panelLoader';

describe('Panel Loader', () => {
  describe('loadRestPanel', () => {
    it('should load panel from REST API', async () => {
      const panelInterface = {
        type: 'REST',
        base: 'http://localhost:5001/api/panels/test',
        panelCol: 'panel'
      };

      const panelData = {
        panel: '0'
      };

      const element = await loadRestPanel(panelInterface, panelData);

      expect(element).toBeInstanceOf(HTMLImageElement);
      expect(element.src).toBe('http://localhost:5001/api/panels/test/0');
    });

    it('should reject on image load error', async () => {
      const panelInterface = {
        type: 'REST',
        base: 'http://localhost:5001/api/panels/test',
        panelCol: 'panel'
      };

      const panelData = {
        panel: 'nonexistent'
      };

      await expect(loadRestPanel(panelInterface, panelData))
        .rejects
        .toThrow('Failed to load panel');
    });

    it('should throw if panel ID is missing', async () => {
      const panelInterface = {
        type: 'REST',
        base: 'http://localhost:5001/api/panels/test',
        panelCol: 'panel'
      };

      const panelData = {};

      await expect(loadRestPanel(panelInterface, panelData))
        .rejects
        .toThrow('Panel ID not found');
    });
  });

  describe('loadFilePanel', () => {
    it('should load panel from file path', async () => {
      const panelInterface = {
        type: 'file',
        panelCol: 'panel',
        extension: 'png'
      };

      const panelData = {
        panel: 'panels/0'
      };

      const element = await loadFilePanel(panelInterface, panelData);

      expect(element).toBeInstanceOf(HTMLImageElement);
      expect(element.src).toContain('panels/0.png');
    });
  });

  describe('loadPanel', () => {
    it('should route to correct loader based on type', async () => {
      const restInterface = { type: 'REST', base: 'http://test', panelCol: 'panel' };
      const restData = { panel: '0' };

      const element = await loadPanel(restInterface, restData);
      expect(element).toBeInstanceOf(HTMLImageElement);
    });

    it('should throw for unsupported types', async () => {
      const badInterface = { type: 'UNKNOWN', panelCol: 'panel' };
      const data = { panel: '0' };

      await expect(loadPanel(badInterface, data))
        .rejects
        .toThrow('Unsupported panel type');
    });
  });
});
```

### Step 4.2: Integration Tests with Python

**File:** `tests/integration/python_integration.test.py`

```python
"""
Integration tests for forked viewer with Python package
"""
import pytest
import subprocess
import time
from pathlib import Path
import requests

@pytest.fixture
def panel_server():
    """Start Flask panel server"""
    server_path = Path(__file__).parent.parent.parent / 'examples' / 'panel_server.py'

    proc = subprocess.Popen(
        ['python3', str(server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(2)

    yield proc

    proc.kill()

def test_viewer_loads_rest_panels(panel_server):
    """Test that forked viewer loads REST panels"""

    # Check server is running
    response = requests.get('http://localhost:5001/api/health')
    assert response.status_code == 200

    # Check panel endpoint works
    response = requests.get('http://localhost:5001/api/panels/minimal_manual/0')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'

def test_python_package_integration():
    """Test full Python package workflow"""
    from trelliscope import Display
    import pandas as pd

    # Create test display
    data = pd.DataFrame({
        'id': [0, 1, 2],
        'value': [0, 10, 20],
        'panel': ['0', '1', '2']
    })

    display = Display(data, name='integration_test')
    display.set_panel_column('panel')
    display.set_panel_interface(
        interface_type='REST',
        base='http://localhost:5001/api/panels/integration_test'
    )

    output_dir = Path('./test_output')
    display.write(output_dir)

    # Verify files created
    assert (output_dir / 'index.html').exists()
    assert (output_dir / 'displays' / 'integration_test' / 'displayInfo.json').exists()

    # Verify panel interface in config
    import json
    with open(output_dir / 'displays' / 'integration_test' / 'displayInfo.json') as f:
        config = json.load(f)

    assert config['panelInterface']['type'] == 'REST'
    assert 'base' in config['panelInterface']
```

### Step 4.3: End-to-End Browser Tests

**File:** `tests/e2e/panel_rendering.spec.js` (Playwright/Cypress)

```javascript
// Using Playwright for browser testing
import { test, expect } from '@playwright/test';

test.describe('Panel Rendering', () => {
  test.beforeEach(async ({ page }) => {
    // Start at viewer page
    await page.goto('http://localhost:5001');
  });

  test('should render REST panels', async ({ page }) => {
    // Wait for viewer to load
    await page.waitForSelector('.panel-card', { timeout: 5000 });

    // Check panel count
    const panelCards = await page.$$('.panel-card');
    expect(panelCards.length).toBe(3);

    // Check images loaded
    const images = await page.$$('.panel-image');
    expect(images.length).toBe(3);

    // Verify image sources
    const firstImgSrc = await images[0].getAttribute('src');
    expect(firstImgSrc).toContain('/api/panels/minimal_manual/0');

    // Check no error states
    const errors = await page.$$('.panel-error');
    expect(errors.length).toBe(0);
  });

  test('should show loading state', async ({ page }) => {
    // Intercept network to slow down
    await page.route('**/api/panels/**', route => {
      setTimeout(() => route.continue(), 1000);
    });

    await page.reload();

    // Should see loading state
    const loading = await page.$('.panel-loading');
    expect(loading).not.toBeNull();
  });

  test('should show error state for failed panels', async ({ page }) => {
    // Intercept to return 404
    await page.route('**/api/panels/**/0', route => {
      route.fulfill({ status: 404 });
    });

    await page.reload();

    // Should see error state
    const error = await page.$('.panel-error');
    expect(error).not.toBeNull();

    const errorText = await error.textContent();
    expect(errorText).toContain('Failed to load');
  });
});
```

---

## Phase 5: Build & Bundle (Days 18-20)

### Step 5.1: Production Build

```bash
# Clean previous build
rm -rf dist/

# Build for production
npm run build

# Verify output
ls -lh dist/
```

**Expected output:**
```
dist/
├── assets/
│   ├── index-[hash].js      # Main viewer bundle
│   ├── index-[hash].css     # Styles
│   └── vendor-[hash].js     # Third-party code
└── index.html               # Entry point (maybe)
```

### Step 5.2: Test Production Build

```bash
# Serve production build
npx serve dist -p 3001

# Open in browser
open http://localhost:3001
```

Verify:
- ✓ Viewer loads
- ✓ Panels render
- ✓ No console errors
- ✓ Good performance

### Step 5.3: Bundle with Python Package

**Directory structure:**
```
py-trelliscope2/
├── trelliscope/
│   ├── viewer/                    # NEW
│   │   ├── index.html.template    # Template with variables
│   │   └── assets/
│   │       ├── index.js           # From dist/assets/index-[hash].js
│   │       └── index.css          # From dist/assets/index-[hash].css
│   └── writers/
│       └── json_writer.py         # Updated to copy viewer
```

**Script to copy viewer:**

**File:** `scripts/bundle_viewer.py`

```python
#!/usr/bin/env python3
"""
Bundle forked viewer with Python package
"""
import shutil
from pathlib import Path

def bundle_viewer():
    # Paths
    fork_dist = Path('path/to/trelliscopejs-lib/dist')
    package_viewer = Path('trelliscope/viewer')

    # Clean existing
    if package_viewer.exists():
        shutil.rmtree(package_viewer)

    package_viewer.mkdir(parents=True)

    # Copy assets
    assets_src = fork_dist / 'assets'
    assets_dst = package_viewer / 'assets'
    shutil.copytree(assets_src, assets_dst)

    # Create index.html template
    index_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{display_name} - Trelliscope</title>
    <link rel="stylesheet" href="assets/index.css">
</head>
<body>
    <div id="trelliscope_root"></div>
    <script type="module">
        import {{ trelliscopeApp }} from './assets/index.js';
        trelliscopeApp('trelliscope_root', './config.json');
    </script>
</body>
</html>
'''

    (package_viewer / 'index.html.template').write_text(index_template)

    print(f'✓ Viewer bundled to {package_viewer}')

if __name__ == '__main__':
    bundle_viewer()
```

---

## Phase 6: Documentation & Release (Days 21-28)

### Step 6.1: Fork Documentation

**File:** `README_PYTHON_FORK.md` in fork repo

```markdown
# Trelliscope Viewer - Python Fork

This is a fork of [trelliscopejs-lib](https://github.com/hafen/trelliscopejs-lib) with added panel rendering support for the [py-trelliscope2](https://github.com/YOUR-ORG/py-trelliscope2) Python package.

## Changes from Upstream

### New Features

1. **REST Panel Support** - Load panels from HTTP API
2. **File Panel Support** - Load panels from static files
3. **Better Error Handling** - Clear error states for panel loading
4. **Python Integration** - Bundled with py-trelliscope2 package

### Modified Files

- `src/utils/panelLoader.js` - Added REST and file panel loaders
- `src/components/Panel/Panel.jsx` - Updated to handle new panel types
- `src/components/Panel/Panel.css` - Added loading/error states
- `src/types/panel.ts` - Added REST and file panel types

### Code Additions

~200 lines of new code for panel loading logic.

## Building

```bash
npm install
npm run build
```

Output: `dist/` directory

## Testing

```bash
npm test                    # Unit tests
npm run test:integration    # Integration tests
npm run test:e2e           # Browser tests
```

## Integration with Python

This viewer is bundled with py-trelliscope2:

```python
from trelliscope import Display

display = Display(data)
display.set_panel_interface(type='REST', base='http://localhost:5001/api/panels/my_display')
display.write()
```

## Maintenance

This fork tracks upstream changes:

```bash
git fetch upstream
git merge upstream/main
```

We aim to keep changes minimal and focused on panel rendering.

## License

Same as upstream: MIT

## Contributing

Please open issues/PRs in the [py-trelliscope2 repository](https://github.com/YOUR-ORG/py-trelliscope2) for Python-specific features.
```

### Step 6.2: Python Package Documentation

Update py-trelliscope2 README:

```markdown
## Panel Rendering

py-trelliscope2 uses a custom fork of trelliscopejs-lib with panel rendering support.

### Supported Panel Types

#### 1. REST API (Recommended)

Serve panels dynamically from a server:

```python
from trelliscope import Display, start_panel_server

# Create display
display = Display(data)
display.set_panel_column('plot')
display.set_panel_interface(
    type='REST',
    base='http://localhost:5001/api/panels/my_display'
)

# Write display
display.write('./output')

# Start server
start_panel_server('./output', port=5001)
```

#### 2. File-based

Use pre-generated image files:

```python
display.set_panel_interface(
    type='file',
    extension='png'
)
```

### Viewer Features

- Interactive grid layout
- Filtering and sorting
- Panel metadata display
- Responsive design
- Error handling

### Custom Viewer

The viewer is a fork of trelliscopejs-lib with Python support.
See [fork repository](https://github.com/YOUR-ORG/trelliscopejs-lib) for details.
```

### Step 6.3: Create Release Checklist

**File:** `RELEASE_CHECKLIST.md`

```markdown
# Release Checklist

## Pre-Release

- [ ] All tests passing (`npm test`)
- [ ] Build succeeds (`npm run build`)
- [ ] Manual testing with Python package
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped in package.json

## Release Steps

1. [ ] Create release branch: `release/v0.7.16-python.1`
2. [ ] Final testing
3. [ ] Tag release: `git tag v0.7.16-python.1`
4. [ ] Push tag: `git push origin v0.7.16-python.1`
5. [ ] Create GitHub release
6. [ ] Bundle with Python package
7. [ ] Test Python package with new viewer
8. [ ] Release Python package

## Post-Release

- [ ] Monitor issues
- [ ] Update documentation site
- [ ] Announce in Python package

## Version Scheme

`<upstream-version>-python.<fork-version>`

Example: `0.7.16-python.1`
```

---

## Quick Start Commands

```bash
# Day 1-2: Setup
git clone https://github.com/YOUR-USERNAME/trelliscopejs-lib.git
cd trelliscopejs-lib
git checkout -b feature/python-panel-support
npm install
npm run dev

# Day 3-5: Analysis
grep -rn "panelInterface" src/
grep -rn "htmlwidget" src/
# Document findings in ARCHITECTURE_NOTES.md

# Day 6-12: Implementation
# Create/modify files as documented above
npm test  # Run tests frequently

# Day 13-17: Testing
npm test
npm run test:integration
npm run test:e2e

# Day 18-20: Build
npm run build
python3 scripts/bundle_viewer.py

# Day 21-28: Documentation & Release
# Create documentation
# Test with Python package
# Create release
```

---

## Success Criteria

✓ All unit tests pass
✓ Integration tests with Python package pass
✓ Browser tests show panels rendering
✓ No console errors
✓ Good performance (< 100ms panel load)
✓ Documentation complete
✓ Examples work

---

## Support & Resources

**Fork Repository:** https://github.com/YOUR-USERNAME/trelliscopejs-lib
**Python Package:** https://github.com/YOUR-ORG/py-trelliscope2
**Original Viewer:** https://github.com/hafen/trelliscopejs-lib

**Contact:** Open issues in py-trelliscope2 repo

---

*Guide created: 2025-11-02*
*Estimated completion: 3-4 weeks*
