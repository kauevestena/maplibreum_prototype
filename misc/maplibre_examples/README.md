# MapLibre Examples Testing Suite

This directory contains a comprehensive testing system to validate that `maplibreum` can reproduce all official MapLibre GL JS examples.

## Purpose

The goal is to systematically test `maplibreum`'s capability to reproduce MapLibre's official examples, providing:
- **Automated validation** of feature coverage
- **Regression testing** for new releases
- **Example conversion** from JavaScript to Python
- **Performance benchmarking** against reference implementations

## Quick Start

### 1. Install Dependencies
```bash
pip install requests beautifulsoup4
```

### 2. Fetch Latest Examples
```bash
cd /home/kaue/maplibreum_prototype
python misc/maplibre_examples/scrapping.py
```

### 3. Check Status
```bash
python -c "import json; data = json.load(open('misc/maplibre_examples/status.json')); print(f'Total examples: {len(data)}'); print(f'Downloaded: {sum(1 for v in data.values() if list(v.values())[0][\"source_status\"])}'); print(f'Implemented: {sum(1 for v in data.values() if list(v.values())[0][\"task_status\"])}')"
```

## Directory Structure

```
misc/maplibre_examples/
├── README.md           # This file - agent instructions
├── scrapping.py        # Fetches examples from maplibre.org
├── status.json         # Tracks progress per example
└── pages/             # Downloaded HTML examples
    ├── 3d-terrain.html
    ├── add-a-marker.html
    └── ... (100+ examples)
```

## Agent Workflow

### For Testing Coverage:
1. **Parse `status.json`** to identify untested examples (`task_status: false`)
2. **Analyze HTML files** in `pages/` to extract JavaScript code
3. **Create equivalent Python/maplibreum code** in `tests/test_examples/`
4. **Update `status.json`** when implementation is complete
5. **Run tests** with `pytest tests/test_examples/`

### For Adding New Examples:
1. **Re-run scrapping** to fetch latest examples
2. **Identify new entries** in `status.json`
3. **Follow conversion workflow** above

### For Regression Testing:
1. **Run all example tests**: `pytest tests/test_examples/ -v`
2. **Check failure patterns** in test output
3. **Update maplibreum core** if systematic failures found

## Status Tracking

The `status.json` file tracks each example with:
```json
{
  "example-name": {
    "example-name": {
      "url": "https://maplibre.org/...",
      "source_status": true,    // HTML downloaded
      "file_path": "misc/...",  // Local file path
      "task_status": false      // Python equivalent created
    }
  }
}
```

## Key Commands for Agents

```bash
# Refresh examples from maplibre.org
python misc/maplibre_examples/scrapping.py

# Count implementation progress
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
total = len(data)
implemented = sum(1 for v in data.values() if list(v.values())[0]['task_status'])
print(f'Progress: {implemented}/{total} ({implemented/total*100:.1f}%)')
"

# Find next example to implement
python -c "
import json
with open('misc/maplibre_examples/status.json') as f:
    data = json.load(f)
for name, info in data.items():
    if not list(info.values())[0]['task_status']:
        print(f'Next: {name}')
        print(f'URL: {list(info.values())[0][\"url\"]}')
        print(f'File: {list(info.values())[0][\"file_path\"]}')
        break
"

# Run specific example test
pytest tests/test_examples/test_<example_name>.py -v

# Run all example tests
pytest tests/test_examples/ -v
```

## Implementation Guidelines

When converting JavaScript examples to Python:
1. **Extract core MapLibre functionality** from HTML/JS
2. **Map JavaScript API calls** to maplibreum equivalents
3. **Preserve visual/functional behavior** 
4. **Create pytest test case** that validates output
5. **Update `task_status: true`** in status.json
6. **Document any limitations** or differences

## Notes for Agents

- **HTML files contain complete examples** with embedded JavaScript
- **Focus on MapLibre-specific code**, ignore generic HTML/CSS
- **Some examples may require new maplibreum features** - document these
- **Maintain test isolation** - each example should be self-contained
- **Use descriptive test names** matching original example names

