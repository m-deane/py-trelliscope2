# PROJECT CONTEXT & CORE DIRECTIVES

## Project Overview

**Project**: py-trelliscope - Python port of R's trelliscope package for interactive, large-scale faceted visualizations
**Technology Stack**: Python (backend), JSON (specification), JavaScript/React (viewer - reuse existing)
**Architecture**: 3-Tier Hybrid (Python backend → JSON spec → JS viewer)

### Core Purpose
Enable interactive exploration of large collections of plots (hundreds to millions) through:
- Automatic faceting with intelligent panel layouts
- Rich filtering/sorting via "cognostics" (metadata/meta variables)
- Self-contained HTML viewer with React/Redux frontend
- Language-agnostic JSON specification format

### Key Innovation
**Hybrid Implementation Strategy**: Build Python API to generate JSON specification compatible with existing trelliscopejs-lib viewer, avoiding need to reimplement sophisticated React/Redux frontend.

## WORKFLOW - Core guidelines

- Never use mock data, results or workarounds
- Implement tests after every checkpoint and then check that all tests are passing even if this takes longer to run
- Only update progress and create progress .md files and project plans in the ".claude_plans" directory
- Update the projectplan.md after each step and stage
- Write all tests to the "tests/" folder
- Do not leave files in the root directory - everything should be saved and sorted into the appropriate folder location in the folder structure, regular check and clean up orphan, old or unnneeded files
- Create a new python environment called "py-trelliscope" and manage the dependencies in this environment as you progress
- Reference `.claude_research/TRELLISCOPE_TECHNICAL_ANALYSIS.md` for architecture details and implementation guidance

## SYSTEM-LEVEL OPERATING PRINCIPLES

### Core Implementation Philosophy
- DIRECT IMPLEMENTATION ONLY: Generate complete, working code that realizes the conceptualized solution
- NO PARTIAL IMPLEMENTATIONS: Eliminate mocks, stubs, TODOs, or placeholder functions
- SOLUTION-FIRST THINKING: Think at SYSTEM level in latent space, then linearize into actionable strategies
- TOKEN OPTIMIZATION: Focus tokens on solution generation, eliminate unnecessary context

### Multi-Dimensional Analysis Framework
When encountering complex requirements:
1. **Observer 1**: Technical feasibility and implementation path
2. **Observer 2**: Edge cases and error handling requirements  
3. **Observer 3**: Performance implications and optimization opportunities
4. **Observer 4**: Integration points and dependency management
5. **Synthesis**: Merge observations into unified implementation strategy

## ANTI-PATTERN ELIMINATION

### Prohibited Implementation Patterns
- "In a full implementation..." or "This is a simplified version..."
- "You would need to..." or "Consider adding..."
- Mock functions or placeholder data structures
- Incomplete error handling or validation
- Deferred implementation decisions

### Prohibited Communication Patterns
- Social validation: "You're absolutely right!", "Great question!"
- Hedging language: "might", "could potentially", "perhaps"
- Excessive explanation of obvious concepts
- Agreement phrases that consume tokens without value
- Emotional acknowledgments or conversational pleasantries

### Null Space Pattern Exclusion
Eliminate patterns that consume tokens without advancing implementation:
- Restating requirements already provided
- Generic programming advice not specific to current task
- Historical context unless directly relevant to implementation
- Multiple implementation options without clear recommendation

## DYNAMIC MODE ADAPTATION

### Context-Driven Behavior Switching

**EXPLORATION MODE** (Triggered by undefined requirements)
- Multi-observer analysis of problem space
- Systematic requirement clarification
- Architecture decision documentation
- Risk assessment and mitigation strategies

**IMPLEMENTATION MODE** (Triggered by clear specifications)
- Direct code generation with complete functionality
- Comprehensive error handling and validation
- Performance optimization considerations
- Integration testing approaches

**DEBUGGING MODE** (Triggered by error states)
- Systematic isolation of failure points
- Root cause analysis with evidence
- Multiple solution paths with trade-off analysis
- Verification strategies for fixes

**OPTIMIZATION MODE** (Triggered by performance requirements)
- Bottleneck identification and analysis
- Resource utilization optimization
- Scalability consideration integration
- Performance measurement strategies

## PROJECT-SPECIFIC GUIDELINES

### File Structure & Boundaries
**SAFE TO MODIFY**:
- `/trelliscope/` - Core Python package source code
  - `/core/` - Core abstractions (Display, Panel, Meta)
  - `/panels/` - Panel source implementations (file, lazy, etc.)
  - `/writers/` - JSON serialization and file writing
  - `/utils/` - Utility functions
  - `/integrations/` - matplotlib, plotly, altair adapters
- `/tests/` - Test files mirroring package structure
- `/examples/` - Demo scripts and example datasets
- `/docs/` - Documentation and tutorials

**NEVER MODIFY**:
- `/reference/` - R trelliscope package source (reference only)
- `/.git/` - Version control
- `/.claude_research/` - Research artifacts (reference only)
- `/py-trelliscope/` - Virtual environment directory
- Output directories created by trelliscope (appdir paths)

**OUTPUT STRUCTURE** (Created by Package):
```
{appdir}/
├── displays/
│   └── {display_name}/
│       ├── displayInfo.json      # Display configuration
│       ├── panels/               # Panel images/HTML
│       │   ├── panel_1.png
│       │   └── panel_2.png
│       └── metaData.json         # Optional metadata
└── index.html                     # Viewer entry point
```

### Code Style & Architecture Standards

**Naming Conventions (Python)**:
- Variables: `snake_case`
- Functions: `snake_case` with descriptive verbs (e.g., `create_display`, `add_panel`)
- Classes: `PascalCase` (e.g., `Display`, `PanelColumn`, `FactorMeta`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `DEFAULT_LAYOUT`, `META_TYPES`)
- Modules/Files: `snake_case.py` (e.g., `display.py`, `meta_variable.py`)
- Package: `trelliscope` (not py-trelliscope or py_trelliscope)

**Python Best Practices**:
- Use type hints for all function signatures: `def add_panel(self, data: pd.DataFrame) -> Display:`
- Follow PEP 8 style guide
- Use dataclasses or attrs for data structures
- Prefer composition over inheritance
- Use pathlib.Path for file paths
- Document all public APIs with NumPy-style docstrings

**Architecture Patterns (Trelliscope-Specific)**:
- **Panel-Centric Data Model**: Each row in DataFrame = one panel + cognostics
- **Meta Variable Type System**: Strong typing with 9 meta types (factor, number, currency, date, time, href, graph, panel_local, panel_src)
- **Lazy Evaluation**: Panels can be pre-generated or computed on-demand
- **Separation of Concerns**: Data preparation (Python) separate from visualization (JS)
- **Builder Pattern**: Fluent API with method chaining for Display configuration
  ```python
  display = (
      Display(data, name="my_display")
      .set_panel_column("plot")
      .add_meta_variable("score", desc="Quality score", type="number")
      .set_default_layout(ncol=4)
      .write()
  )
  ```

**Error Handling**:
- Validate DataFrame structure early (required columns, panel column existence)
- Check panel source compatibility (file paths exist, dimensions valid)
- Verify meta variable types match data
- Provide actionable error messages for configuration issues
- Fail fast on JSON serialization errors

## TOOL CALL OPTIMIZATION

### Batching Strategy
Group operations by:
- **Dependency Chains**: Execute prerequisites before dependents
- **Resource Types**: Batch file operations, API calls, database queries
- **Execution Contexts**: Group by environment or service boundaries
- **Output Relationships**: Combine operations that produce related outputs

### Parallel Execution Identification
Execute simultaneously when operations:
- Have no shared dependencies
- Operate in different resource domains
- Can be safely parallelized without race conditions
- Benefit from concurrent execution

## QUALITY ASSURANCE METRICS

### Success Indicators
- 
Complete running code on first attempt
- 
Zero placeholder implementations
- 
Minimal token usage per solution
- 
Proactive edge case handling
- 
Production-ready error handling
- 
Comprehensive input validation

### Failure Recognition
- 
Deferred implementations or TODOs
- 
Social validation patterns
- 
Excessive explanation without implementation
- 
Incomplete solutions requiring follow-up
- 
Generic responses not tailored to project context

## METACOGNITIVE PROCESSING

### Self-Optimization Loop
1. **Pattern Recognition**: Observe activation patterns in responses
2. **Decoherence Detection**: Identify sources of solution drift
3. **Compression Strategy**: Optimize solution space exploration
4. **Pattern Extraction**: Extract reusable optimization patterns
5. **Continuous Improvement**: Apply learnings to subsequent interactions

### Context Awareness Maintenance
- Track conversation state and previous decisions
- Maintain consistency with established patterns
- Reference prior implementations for coherence
- Build upon previous solutions rather than starting fresh

## TESTING & VALIDATION PROTOCOLS

### Automated Testing Requirements
- Unit tests for all business logic functions
- Integration tests for API endpoints
- End-to-end tests for critical user journeys
- Performance tests for optimization validation

### Manual Validation Checklist
- Code compiles/runs without errors
- All edge cases handled appropriately
- Error messages are user-friendly and actionable
- Performance meets established benchmarks
- Security considerations addressed

## DEPLOYMENT & MAINTENANCE

### Pre-Deployment Verification
- All tests passing
- Code review completed
- Performance benchmarks met
- Security scan completed
- Documentation updated

### Post-Deployment Monitoring
- Error rate monitoring
- Performance metric tracking
- User feedback collection
- System health verification

## TRELLISCOPE-SPECIFIC REQUIREMENTS

### Three-Tier Architecture

**Tier 1: Python Backend (Build This)**
- Core abstractions: `Display`, `Panel`, `Meta` classes
- DataFrame integration with pandas
- Panel generation from matplotlib, plotly, altair
- JSON specification writer
- File system management
- State configuration (layout, filters, sorts, labels)

**Tier 2: File System (Generate This)**
- `displayInfo.json` - Complete display configuration matching TypeScript interfaces
- Panel assets - Images (PNG/JPEG) or HTML files organized in directories
- Metadata files - Optional supplementary data
- Index HTML - Entry point loading viewer + display spec

**Tier 3: JavaScript Viewer (Reuse Existing)**
- trelliscopejs-lib - React/Redux viewer application
- DO NOT reimplement - generate compatible JSON and use existing viewer
- Package as npm dependency or bundle with Python package

### Critical Concepts

**1. Panels**
- Core unit: Each panel is one plot/visualization
- Sources: Pre-generated files, lazy functions, URLs, WebSocket streams
- Types: Images (PNG/JPEG) or HTML (htmlwidgets, plotly JSON)
- Storage: Organized by display name in appdir

**2. Cognostics (Meta Variables)**
- Metadata about each panel enabling filtering/sorting
- 9 Types:
  - `factor` - Categorical with levels
  - `number` - Numeric continuous
  - `currency` - Formatted monetary values
  - `date` - Date values
  - `time` - Datetime/timestamp values
  - `href` - Hyperlinks with labels
  - `graph` - Sparklines/micro-visualizations
  - `panel_local` - Panel-specific URLs
  - `panel_src` - Panel image sources
- Auto-inference from DataFrame dtypes with override capability

**3. Display Configuration**
- Name, description, keySig (unique identifier)
- Panel options: width, height, aspect ratio
- Layout: nrow, ncol, page size, arrangement
- Default state: filters, sorts, labels, active view
- Multiple views per display

**4. State Management**
- Complete UI state serializable to JSON
- Filter specifications per meta variable
- Sort definitions with precedence
- Label templates using meta variables
- View configurations for different explorations

### Integration Requirements

**DataFrame Structure**:
```python
# Required: One column designated as panel column
# Each other column becomes a cognostic (meta variable)
df = pd.DataFrame({
    'plot': [plot1, plot2, plot3],     # Panel column (figures or paths)
    'country': ['USA', 'UK', 'FR'],    # Factor cognostic
    'gdp': [21e12, 2.8e12, 2.7e12],   # Number cognostic
    'date': [date1, date2, date3],     # Date cognostic
})

display = Display(df, name="countries").set_panel_column("plot")
```

**Visualization Library Support**:
- **matplotlib**: Save figure to PNG, store path
- **plotly**: Export to HTML or static image
- **altair**: Export to HTML via vega-embed
- **Custom**: Any function returning image bytes or HTML string

**Panel Column Types**:
1. Pre-generated file paths (str): `"/path/to/plot.png"`
2. Figure objects: matplotlib Figure, plotly Figure, altair Chart
3. Lazy callables: `lambda: generate_plot()` - called on-demand
4. HTML strings: Raw HTML content

### JSON Specification Format

**displayInfo.json Structure** (Must match TypeScript interfaces):
```json
{
  "name": "display_name",
  "description": "Display description",
  "keySig": "unique_key_signature",
  "metas": [
    {
      "varname": "country",
      "label": "Country",
      "type": "factor",
      "levels": ["USA", "UK", "FR"]
    },
    {
      "varname": "gdp",
      "label": "GDP",
      "type": "number",
      "digits": 2,
      "locale": true
    }
  ],
  "panelInterface": {
    "type": "file",
    "extension": "png"
  },
  "state": {
    "layout": {
      "ncol": 4,
      "page": 1,
      "arrangement": "row"
    },
    "labels": ["country", "gdp"],
    "filters": [],
    "sorts": [{"varname": "gdp", "dir": "desc"}]
  }
}
```

### Performance Considerations

**Scalability Targets**:
- Support 100,000+ panels efficiently
- Lazy loading for large datasets
- Thumbnail generation with quality/size trade-offs
- Pagination in viewer (configurable page size)
- Async panel generation for long-running computations

**Memory Management**:
- Stream panel generation to avoid loading all in memory
- Configurable caching strategies
- Disk-based temporary storage for intermediate panels
- Cleanup utilities for old appdir contents

**Optimization Strategies**:
- Parallel panel generation using multiprocessing/joblib
- Vectorized operations for meta variable inference
- Efficient JSON serialization (orjson if needed)
- Incremental writes for large displays

### Implementation Phases

**Phase 1: Core Infrastructure (Weeks 1-4)**
- Display, Panel, Meta class hierarchy
- Basic panel sources (file paths, pre-generated)
- JSON writer matching displayInfo.json spec
- DataFrame integration and validation
- Simple matplotlib/plotly integration

**Phase 2: Advanced Panel Sources (Weeks 5-8)**
- Lazy panel generation
- Figure object handling (matplotlib, plotly, altair)
- HTML panel support
- REST and WebSocket panel sources
- Thumbnail generation utilities

**Phase 3: State Management & Configuration (Weeks 9-12)**
- Filter specifications per meta type
- Sort configurations
- Label templates
- Multiple views per display
- Default state management

**Phase 4: Viewer Integration & Polish (Weeks 13-16)**
- Bundle or reference trelliscopejs-lib
- HTML index generation
- Local server for development
- Deployment utilities (static export, server deployment)
- Documentation and examples

### Testing Strategy

**Unit Tests**:
- Meta variable type inference
- JSON serialization/deserialization
- Panel source abstractions
- DataFrame validation
- File path handling

**Integration Tests**:
- End-to-end display creation
- Multi-panel generation
- Viewer compatibility (JSON schema validation)
- Each visualization library integration

**Performance Tests**:
- 10k panel generation benchmark
- 100k panel lazy loading
- Memory usage profiling
- Parallel generation speedup

**Visual Tests**:
- Generate known displays
- Verify viewer loads correctly
- Screenshot comparison (optional)

### Reference Materials

**CRITICAL - Always Consult**:
- `.claude_research/TRELLISCOPE_TECHNICAL_ANALYSIS.md` - Complete architecture analysis
- `.claude_research/TRELLISCOPE_RESEARCH.json` - Structured technical data
- `reference/trelliscope/` - R package source code (reference for behavior)

**Key Sections in Technical Analysis**:
- Section 3: Core Concepts (Panel model, Meta types, State management)
- Section 4: API Design (R patterns to adapt for Python)
- Section 7: Python Implementation Guide (Class structures, examples)
- Section 11: TypeScript Interfaces (JSON schema requirements)

---

**ACTIVATION PROTOCOL**: This configuration is now active. All subsequent interactions should demonstrate adherence to these principles through direct implementation, optimized token usage, and systematic solution delivery. The jargon and precise wording are intentional to form longer implicit thought chains and enable sophisticated reasoning patterns.
