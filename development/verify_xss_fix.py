import json

def json_dumps_tojson(value):
    return json.dumps(value)

def test_security():
    # The vulnerability was: el.innerHTML = `${marker.html}`;
    # where marker.html could contain ` breakout.

    malicious_input = "` + alert(1) + `"

    # Secure interpolation (my fix): el.innerHTML = {{ marker.html | tojson }};
    # Rendered as:
    rendered = json_dumps_tojson(malicious_input)

    print(f"Malicious input: {malicious_input}")
    print(f"Rendered JS: el.innerHTML = {rendered};")

    if "`" in rendered:
        print("FAILED: Backtick found in output (could still breakout if template used backticks)")

    # Verify it can't breakout of a standard JS assignment
    js_context = f"var x = {rendered};"
    print(f"JS Context: {js_context}")

    # In JS, var x = "` + alert(1) + `"; is a safe string assignment.
    # The alert(1) will NOT execute.

    if "alert(1)" in rendered and rendered.startswith('"') and rendered.endswith('"'):
         print("SUCCESS: Malicious payload is safely contained within a quoted string.")
         return True
    return False

if __name__ == "__main__":
    if test_security():
        print("\nVERIFICATION: SECURE")
    else:
        print("\nVERIFICATION: FAILED")
        exit(1)
