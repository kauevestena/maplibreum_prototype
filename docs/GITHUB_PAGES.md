# GitHub Pages Examples Deployment

This repository includes a GitHub Actions workflow that automatically converts Jupyter notebooks in the `examples/` folder to HTML and deploys them to GitHub Pages as a showcase/gallery.

## How to Deploy Examples

The deployment runs automatically after a push to `main`. It can also be
started manually when you need to rebuild the gallery without a new commit:

1. Go to the repository's **Actions** tab
2. Select the "Documentation Build" workflow
3. Click **Run workflow**
4. Optionally enable debug mode for more verbose output
5. Click the green **Run workflow** button

## What the Workflow Does

1. **Setup Environment**: Installs Python 3.11 and required dependencies including `maplibreum`, `jupyter`, and `nbconvert`

2. **Execute Notebooks**: Runs each Jupyter notebook in the `examples/` folder:
   - Executes all cells to generate outputs and interactive maps
   - Converts notebooks to HTML format
   - Stops the build if execution fails, preventing broken examples from being published

3. **Create Gallery**: Generates a beautiful index page that showcases all examples with descriptions

4. **Deploy**: Publishes the HTML files to GitHub Pages

## Examples Included

The gallery follows a seven-part learning path: quickstart, data-driven styling,
thematic mapping, terrain and PMTiles, export-safe interaction, clustering
for larger point collections, and a planet-scale PMTiles basemap. See the
[examples guide](https://github.com/kauevestena/maplibreum_prototype/blob/main/examples/README.md)
for the current notebook descriptions.

## Accessing the Deployed Examples

Once deployed, the examples will be available at:
`https://[username].github.io/[repository-name]/`

For this repository:
`https://kauevestena.github.io/maplibreum_prototype/`

## Requirements

- GitHub Pages must be enabled in repository settings
- Workflow requires `contents: read`, `pages: write`, and `id-token: write` permissions (included in workflow)
- Python 3.11 with pip package manager

## Troubleshooting

- If a notebook fails, the workflow fails and preserves the error in the Actions log
- Check the Actions log for detailed error messages
- Run `pytest tests/test_notebooks.py -v` before pushing notebook changes
- Ensure all notebooks have valid Python code and deterministic teaching data
- The workflow includes a 5-minute timeout per notebook execution
