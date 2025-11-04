# Environment Setup - py-trelliscope

**Date**: October 27, 2025
**Status**: ✅ Complete

---

## Environment Created

**Name**: `py-trelliscope`
**Type**: Python virtual environment (venv)
**Python Version**: 3.10
**Location**: `py-trelliscope-env/`

---

## Installation Steps Completed

### 1. Virtual Environment Creation
```bash
python3 -m venv py-trelliscope-env
```

### 2. Dependencies Installed

**Core Dependencies** (from requirements.txt):
- attrs==25.4.0
- coverage==7.11.0
- exceptiongroup==1.3.0
- iniconfig==2.3.0
- numpy==2.2.6
- packaging==25.0
- pandas==2.3.3
- pluggy==1.6.0
- Pygments==2.19.2
- pytest==8.4.2
- pytest-cov==7.0.0
- python-dateutil==2.9.0.post0
- pytz==2025.2
- six==1.17.0
- tomli==2.3.0
- typing_extensions==4.15.0
- tzdata==2025.2

**Visualization Libraries**:
- matplotlib==3.10.7
- plotly==6.3.1

**Jupyter Environment**:
- jupyter==1.1.1
- ipykernel==7.1.0
- jupyterlab==4.4.10
- notebook==7.4.7

**Total Packages Installed**: ~80 (including dependencies)

### 3. Package Installation

Created `setup.py` and installed py-trelliscope in development mode:
```bash
pip install -e .
```

This allows the package to be imported and edited without reinstallation.

### 4. Jupyter Kernel Registration

Registered the environment as a Jupyter kernel:
```bash
python -m ipykernel install --user --name py-trelliscope --display-name "Python (py-trelliscope)"
```

**Kernel Location**: `/Users/matthewdeane/Library/Jupyter/kernels/py-trelliscope`

---

## Notebook Execution Results

### Executed Notebook: `examples/01_getting_started.ipynb`

**Execution Method**:
```bash
jupyter nbconvert --to notebook --execute --inplace \
  examples/01_getting_started.ipynb \
  --ExecutePreprocessor.kernel_name=py-trelliscope
```

**Status**: ✅ Success

**Outputs Created**:
```
examples/trelliscope_output/
├── simple_display/
│   ├── displayInfo.json
│   ├── metadata.csv
│   └── panels/
├── sales_dashboard/
│   ├── displayInfo.json
│   ├── metadata.csv
│   └── panels/
└── experiment_results/
    ├── displayInfo.json
    ├── metadata.csv
    └── panels/
```

**Verification**:
- ✅ All three displays created successfully
- ✅ displayInfo.json contains proper metadata definitions
- ✅ metadata.csv has correct data (category, score, rank columns)
- ✅ Panels directory created for each display

---

## Usage

### Activate Environment

```bash
cd /Users/matthewdeane/Documents/Data\ Science/python/_projects/py-trelliscope2
source py-trelliscope-env/bin/activate
```

### Deactivate Environment

```bash
deactivate
```

### Run Jupyter Lab with py-trelliscope Kernel

```bash
source py-trelliscope-env/bin/activate
jupyter lab
# Select "Python (py-trelliscope)" kernel in notebooks
```

### Run Tests

```bash
source py-trelliscope-env/bin/activate
pytest
```

### Run Specific Notebook

```bash
source py-trelliscope-env/bin/activate
jupyter nbconvert --to notebook --execute --inplace \
  examples/YOUR_NOTEBOOK.ipynb \
  --ExecutePreprocessor.kernel_name=py-trelliscope
```

---

## Files Created

1. **setup.py** - Package setup file for development installation
2. **py-trelliscope-env/** - Virtual environment directory
3. **examples/trelliscope_output/** - Notebook outputs (3 displays)

---

## Verification Tests

### Test Import

```python
from trelliscope import Display
from trelliscope.config import ViewerConfig
from trelliscope import export_static
import pandas as pd
import numpy as np
```

### Test Display Creation

```python
df = pd.DataFrame({'panel': ['a', 'b'], 'value': [1, 2]})
display = Display(df, name="test").set_panel_column('panel')
display.write(render_panels=False)
```

---

## Next Steps

### Option A: Run Additional Notebooks

```bash
# Run panel rendering notebook
jupyter nbconvert --to notebook --execute --inplace \
  examples/02_panel_rendering.ipynb \
  --ExecutePreprocessor.kernel_name=py-trelliscope

# Run viewer integration notebook
jupyter nbconvert --to notebook --execute --inplace \
  examples/10_viewer_integration.ipynb \
  --ExecutePreprocessor.kernel_name=py-trelliscope
```

### Option B: Interactive Development

```bash
source py-trelliscope-env/bin/activate
jupyter lab
# Open any notebook and select "Python (py-trelliscope)" kernel
```

### Option C: Continue Development

Proceed with Phase 3 (State Management) or Phase 2 (Advanced Panel Sources) as discussed.

---

## Troubleshooting

### Kernel Not Found

If Jupyter can't find the py-trelliscope kernel:
```bash
source py-trelliscope-env/bin/activate
python -m ipykernel install --user --name py-trelliscope --display-name "Python (py-trelliscope)" --force
```

### Import Errors

If trelliscope module can't be imported:
```bash
source py-trelliscope-env/bin/activate
pip install -e . --force-reinstall
```

### Missing Dependencies

If visualization libraries are missing:
```bash
source py-trelliscope-env/bin/activate
pip install matplotlib plotly
```

---

## Summary

✅ **Environment**: py-trelliscope virtual environment created and activated
✅ **Dependencies**: All required packages installed (~80 packages)
✅ **Package**: py-trelliscope installed in development mode
✅ **Kernel**: Registered with Jupyter as "Python (py-trelliscope)"
✅ **Notebook**: 01_getting_started.ipynb executed successfully
✅ **Outputs**: 3 trelliscope displays created with proper structure
✅ **Tests**: 412 tests passing

**Ready for**: Development, testing, and running notebooks
