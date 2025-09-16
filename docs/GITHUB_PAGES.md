# GitHub Pages Examples Deployment

This repository includes a GitHub Actions workflow that automatically converts Jupyter notebooks in the `examples/` folder to HTML and deploys them to GitHub Pages as a showcase/gallery.

## How to Deploy Examples

The deployment is triggered manually to give full control over when examples are published:

1. Go to the repository's **Actions** tab
2. Select the "Deploy Examples to GitHub Pages" workflow
3. Click **Run workflow**
4. Optionally enable debug mode for more verbose output
5. Click the green **Run workflow** button

## What the Workflow Does

1. **Setup Environment**: Installs Python 3.11 and required dependencies including `maplibreum`, `jupyter`, and `nbconvert`

2. **Execute Notebooks**: Runs each Jupyter notebook in the `examples/` folder:
   - Executes all cells to generate outputs and interactive maps
   - Converts notebooks to HTML format
   - Handles errors gracefully - if execution fails, converts without execution

3. **Create Gallery**: Generates a beautiful index page that showcases all examples with descriptions

4. **Deploy**: Publishes the HTML files to GitHub Pages

## Examples Included

The following notebooks are automatically processed:

- **Creative MapLibreum Examples & Tutorials**: Comprehensive showcase of features
- **Basic Usage Examples**: Fundamental patterns for creating maps  
- **New Features Demo**: Latest MapLibreum capabilities
- **Event Handling**: Interactive callbacks and user interactions

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

- If a notebook fails to execute, it will still be converted to HTML without execution
- Check the Actions log for detailed error messages
- Ensure all notebooks have valid Python code and required data
- The workflow includes a 5-minute timeout per notebook execution