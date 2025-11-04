# Trelliscope Viewer Fork Strategy

## Date: 2025-11-02
## Status: Planning Phase

---

## Overview

This document outlines the strategy for forking trelliscopejs-lib and adding panel rendering support for the Python py-trelliscope2 package.

## Problem Statement

trelliscopejs-lib v0.7.16 does not support rendering panels for any panel interface type except `htmlwidget`. We need to add support for REST API panels to enable the Python package to work.

## Proof of Concept

**File:** `examples/output/minimal_viewer.html`

A working minimal viewer (~200 lines of JavaScript) that demonstrates the core functionality needed:

```javascript
if (panelInterface.type === 'REST') {
    const panelId = data[panelInterface.panelCol];
    const imageUrl = `${panelInterface.base}/${panelId}`;

    const img = document.createElement('img');
    img.src = imageUrl;
    container.appendChild(img);
}
```

This POC proves the concept is viable and shows exactly what needs to be added to the viewer.

## Fork Strategy

### Phase 1: Repository Setup (Week 1)

#### 1.1 Fork Repository
```bash
# On GitHub
Fork: hafen/trelliscopejs-lib → your-username/trelliscopejs-lib

# Clone locally
git clone https://github.com/your-username/trelliscopejs-lib.git
cd trelliscopejs-lib

# Add upstream remote
git remote add upstream https://github.com/hafen/trelliscopejs-lib.git
```

#### 1.2 Create Feature Branch
```bash
git checkout -b feature/rest-panel-support
```

#### 1.3 Development Environment Setup
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Phase 2: Code Analysis (Week 1)

#### 2.1 Identify Key Files

Based on React/Redux architecture, likely files:

```
src/
├── components/
│   └── Panel/
│       ├── Panel.jsx          # Main panel component
│       └── PanelRenderer.jsx  # Panel rendering logic
├── store/
│   └── panels/
│       ├── panelActions.js    # Panel data fetching
│       └── panelReducers.js   # Panel state management
└── utils/
    └── panelLoader.js         # Panel loading utilities
```

#### 2.2 Search for Panel Interface Handling

Search codebase for:
```bash
grep -r "panelInterface" src/
grep -r "htmlwidget" src/
grep -r "panel.*type" src/
```

#### 2.3 Locate Rendering Logic

Find where panels are actually rendered to DOM:
```bash
grep -r "createElement\|appendChild" src/components/Panel
grep -r "img\|Image" src/
```

### Phase 3: Implementation (Week 2)

#### 3.1 Add REST Panel Support

**File:** `src/utils/panelLoader.js` (example)

```javascript
// BEFORE (current code - only supports htmlwidget)
export function loadPanel(panelInterface, panelData) {
  if (panelInterface.type === 'htmlwidget') {
    return loadHtmlWidget(panelInterface, panelData);
  }
  // Currently returns nothing for other types
  return null;
}

// AFTER (add REST support)
export function loadPanel(panelInterface, panelData) {
  switch (panelInterface.type) {
    case 'htmlwidget':
      return loadHtmlWidget(panelInterface, panelData);

    case 'REST':
      return loadRestPanel(panelInterface, panelData);

    case 'file':
    case 'panel_local':
      return loadFilePanel(panelInterface, panelData);

    default:
      console.warn(`Unsupported panel type: ${panelInterface.type}`);
      return null;
  }
}

// NEW FUNCTION
function loadRestPanel(panelInterface, panelData) {
  const panelId = panelData[panelInterface.panelCol];
  const imageUrl = `${panelInterface.base}/${panelId}`;

  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load panel: ${imageUrl}`));

    img.src = imageUrl;
  });
}

// BONUS: File-based panel support
function loadFilePanel(panelInterface, panelData) {
  const panelPath = panelData[panelInterface.panelCol];

  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load panel: ${panelPath}`));

    img.src = panelPath;
  });
}
```

#### 3.2 Update Panel Component

**File:** `src/components/Panel/Panel.jsx` (example)

```jsx
import React, { useEffect, useState } from 'react';
import { loadPanel } from '../../utils/panelLoader';

export function Panel({ panelInterface, panelData }) {
  const [imageElement, setImageElement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    loadPanel(panelInterface, panelData)
      .then(img => {
        setImageElement(img);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [panelInterface, panelData]);

  if (loading) return <div className="panel-loading">Loading...</div>;
  if (error) return <div className="panel-error">{error}</div>;

  return (
    <div className="panel-container">
      {imageElement && <img src={imageElement.src} alt="Panel" />}
    </div>
  );
}
```

### Phase 4: Testing (Week 2-3)

#### 4.1 Unit Tests

```javascript
// tests/panelLoader.test.js
import { loadPanel } from '../src/utils/panelLoader';

describe('Panel Loader', () => {
  it('should load REST panels', async () => {
    const panelInterface = {
      type: 'REST',
      base: 'http://localhost:5001/api/panels/test',
      panelCol: 'panel'
    };

    const panelData = {
      panel: '0'
    };

    const img = await loadPanel(panelInterface, panelData);
    expect(img).toBeInstanceOf(Image);
    expect(img.src).toBe('http://localhost:5001/api/panels/test/0');
  });

  it('should load file-based panels', async () => {
    const panelInterface = {
      type: 'file',
      panelCol: 'panel'
    };

    const panelData = {
      panel: 'panels/0.png'
    };

    const img = await loadPanel(panelInterface, panelData);
    expect(img).toBeInstanceOf(Image);
    expect(img.src).toContain('panels/0.png');
  });
});
```

#### 4.2 Integration Tests

Test with Python package:

```python
# test_viewer_fork.py
from trelliscope import Display
import pandas as pd

# Create test display
data = pd.DataFrame({
    'id': [0, 1, 2],
    'value': [0, 10, 20],
    'panel': ['0', '1', '2']
})

display = Display(data, name='fork_test')
display.set_panel_column('panel')
display.set_panel_interface(
    interface_type='REST',
    base='http://localhost:5001/api/panels/fork_test'
)
display.write('./test_output')

# Verify viewer loads and renders panels
```

### Phase 5: Build & Bundle (Week 3)

#### 5.1 Production Build

```bash
npm run build
```

Outputs to `dist/`:
- `assets/index.js` - Main viewer code
- `assets/index.css` - Styles

#### 5.2 Integration with Python Package

```
py-trelliscope2/
├── trelliscope/
│   ├── viewer/              # NEW: Bundled viewer
│   │   ├── index.html
│   │   ├── assets/
│   │   │   ├── index.js     # Forked viewer build
│   │   │   └── index.css
│   │   └── config.json.template
│   └── writers/
│       └── json_writer.py   # Copy viewer files to output
```

#### 5.3 Update Python Package

```python
# trelliscope/writers/json_writer.py
import shutil
from pathlib import Path

class JSONWriter:
    def write(self, display, output_dir):
        # ... existing code ...

        # Copy forked viewer
        viewer_src = Path(__file__).parent.parent / 'viewer'
        viewer_dst = output_dir

        shutil.copy(viewer_src / 'index.html', viewer_dst)
        shutil.copytree(viewer_src / 'assets', viewer_dst / 'assets')

        # ... write displayInfo.json etc ...
```

### Phase 6: Documentation (Week 4)

#### 6.1 Fork Documentation

**File:** `PYTHON_FORK_README.md` in forked repo

```markdown
# Trelliscope Viewer - Python Fork

This is a fork of trelliscopejs-lib with added support for REST and file-based panel rendering for use with the py-trelliscope2 Python package.

## Changes from Upstream

1. Added REST panel interface support
2. Added file-based panel interface support
3. Improved error handling for panel loading

## Building

npm install
npm run build

## Testing

npm test
npm run test:integration

## Integration with Python

This viewer is bundled with py-trelliscope2. See Python package documentation for usage.
```

#### 6.2 Python Package Documentation

Update py-trelliscope2 docs:

```markdown
## Panel Rendering

py-trelliscope2 uses a forked version of trelliscopejs-lib with panel rendering support.

### Supported Panel Types

1. **REST API** (recommended)
   - Panels served dynamically from Flask server
   - Best for large displays and lazy generation

2. **File-based**
   - Pre-generated PNG/JPG files
   - Good for small displays or static exports
```

## Maintenance Strategy

### 1. Track Upstream Changes

```bash
# Periodically sync with upstream
git fetch upstream
git merge upstream/main

# Resolve conflicts in fork-specific files
# Test thoroughly after merge
```

### 2. Minimize Divergence

- Keep changes focused on panel rendering
- Don't modify other viewer features
- Document all modifications clearly
- Use feature flags if possible

### 3. Version Management

```json
// package.json
{
  "name": "trelliscopejs-lib-python",
  "version": "0.7.16-python.1",
  "description": "Fork with Python panel support"
}
```

Versioning: `<upstream-version>-python.<fork-version>`

### 4. Automated Testing

Set up CI/CD:

```yaml
# .github/workflows/test.yml
name: Test Fork
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test
      - run: npm run build
      - name: Test with Python package
        run: |
          pip install py-trelliscope2
          python tests/integration_test.py
```

## Timeline & Resources

### Estimated Effort

| Phase | Duration | Effort |
|-------|----------|--------|
| Fork & Setup | 2-3 days | Low |
| Code Analysis | 3-4 days | Medium |
| Implementation | 5-7 days | High |
| Testing | 4-5 days | Medium |
| Build & Bundle | 2-3 days | Low |
| Documentation | 3-4 days | Medium |
| **Total** | **3-4 weeks** | **~120 hours** |

### Skills Required

1. **JavaScript/React** - Moderate to advanced
2. **Redux** - Basic understanding
3. **Build tools** (webpack/vite) - Basic
4. **Python packaging** - Basic
5. **Testing** (Jest, pytest) - Basic

### Resources Needed

1. Developer with React experience (1 FTE for 1 month)
2. Testing environment (local + CI/CD)
3. GitHub account for fork
4. npm account for potential publishing

## Success Criteria

✓ REST panels render correctly
✓ File-based panels render correctly
✓ All existing tests pass
✓ New tests for panel types pass
✓ Builds without errors
✓ Integrates with Python package
✓ Documentation complete
✓ Example gallery works

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex codebase | High | Medium | Start with POC, incremental changes |
| Upstream conflicts | Medium | Low | Minimal changes, good documentation |
| Breaking changes | Low | High | Comprehensive testing, version pinning |
| Maintenance burden | Medium | Medium | Automated testing, clear documentation |

## Alternative: Minimal Changes

If forking seems too complex, consider:

1. **Wrapper approach** - Keep original viewer, add panel loading shim
2. **Monkey patching** - Override panel rendering at runtime
3. **External panel loader** - Separate component that works with viewer

But these are all more fragile than a proper fork.

## Next Steps

1. ✓ Create POC (minimal_viewer.html) - DONE
2. ⬜ Test POC with REST server
3. ⬜ If POC successful, fork repository
4. ⬜ Begin Phase 1: Repository setup
5. ⬜ Continue through phases 2-6

## Conclusion

Forking is the most sustainable solution for adding panel rendering to trelliscopejs-lib. The POC demonstrates feasibility, and the phased approach minimizes risk.

**Recommended:** Proceed with fork implementation.
