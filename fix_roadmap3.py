import re

content = open('development/maplibre_examples/march_2026_roadmap.md').read()

# For all files that contain "_with_python_api", change the checkbox to [x]
import glob
for file in glob.glob('tests/test_examples/*.py'):
    with open(file) as f:
        if '_with_python_api' in f.read():
            basename = file.split('/')[-1]
            content = content.replace(f"- [ ] `tests/test_examples/{basename}`", f"- [x] `tests/test_examples/{basename}`")

with open('development/maplibre_examples/march_2026_roadmap.md', 'w') as f:
    f.write(content)
