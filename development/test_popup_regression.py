from jinja2 import Environment, FileSystemLoader
import json
import os

# Mocking the Environment setup from core.py
template_dir = "maplibreum/templates"
env = Environment(loader=FileSystemLoader(template_dir))
env.filters["tojson"] = lambda value: json.dumps(value)
template = env.get_template("map_template.html")

# Mock data matching failing tests
popups = [{"options": {}, "html": "<h1>Hello World!</h1>"}]

rendered = template.render(popups=popups, markers=[], controls=[], title="Test", map_options={}, map_id="map_0")

if "<h1>Hello World!</h1>" in rendered:
    print("SUCCESS: Literal HTML preserved in output (Regression Fixed)")
else:
    print("FAILED: Literal HTML missing or escaped in output")
    if "&lt;h1&gt;" in rendered:
         print("Found escaped HTML: &lt;h1&gt;")
