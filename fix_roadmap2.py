content = open('development/maplibre_examples/march_2026_roadmap.md').read()
content = content.replace("- [ ] `tests/test_examples/test_update_a_feature_in_realtime_with_python_api.py`\n", "")
with open('development/maplibre_examples/march_2026_roadmap.md', 'w') as f:
    f.write(content)
