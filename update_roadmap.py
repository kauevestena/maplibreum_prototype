content = open('development/maplibre_examples/march_2026_roadmap.md').read()
for f in ["test_pmtiles_source_and_protocol.py", "test_geocode_with_nominatim.py", "test_filter_layer_symbols_using_global_state.py"]:
    content = content.replace(f"- [ ] `tests/test_examples/{f}`", f"- [x] `tests/test_examples/{f}`")

with open('development/maplibre_examples/march_2026_roadmap.md', 'w') as f:
    f.write(content)
