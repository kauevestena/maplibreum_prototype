"""Parity test for the fly-to-a-location-based-on-scroll-position example."""

from maplibreum.core import Map


def test_fly_to_a_location_based_on_scroll_position():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[-0.15591514, 51.51830379],
        zoom=15.5,
        bearing=27,
        pitch=45,
    )

    m.custom_css = "\n".join(
        [
            f"#{m.map_id} {{ position: fixed; width: 50%; }}",
            ".maplibreum-story {",
            "    width: 50%;",
            "    margin-left: 50%;",
            "    font-family: sans-serif;",
            "    overflow-y: scroll;",
            "    background-color: #fafafa;",
            "}",
            ".maplibreum-story section {",
            "    padding: 25px 50px;",
            "    line-height: 25px;",
            "    border-bottom: 1px solid #ddd;",
            "    opacity: 0.25;",
            "    font-size: 13px;",
            "}",
            ".maplibreum-story section.active { opacity: 1; }",
            ".maplibreum-story section:last-child { border-bottom: none; margin-bottom: 200px; }",
        ]
    )

    story_html = """
    <section id="baker" class="active">
        <h3>221b Baker St.</h3>
        <p>November 1895. London is shrouded in fog and Sherlock Holmes and Watson await a new case.</p>
    </section>
    <section id="aldgate">
        <h3>Aldgate Station</h3>
        <p>Arthur Cadogan West is found dead on the tracks at Aldgate Station with submarine plans missing.</p>
    </section>
    <section id="london-bridge">
        <h3>London Bridge</h3>
        <p>Holmes dispatches a telegram to Mycroft at London Bridge to gather intelligence on foreign spies.</p>
    </section>
    <section id="woolwich">
        <h3>Woolwich Arsenal</h3>
        <p>Investigations reveal West lacked the keys required to steal the plans, raising new suspicions.</p>
    </section>
    <section id="gloucester">
        <h3>Gloucester Road</h3>
        <p>Holmes inspects Caulfield Gardens, noting trains pause beneath the suspect's apartment windows.</p>
    </section>
    <section id="caulfield-gardens">
        <h3>13 Caulfield Gardens</h3>
        <p>Evidence suggests the murderer loaded West onto a train at Caulfield Gardens before the fatal fall.</p>
    </section>
    <section id="telegraph">
        <h3>The Daily Telegraph</h3>
        <p>Holmes places a classified ad to lure the conspirators into revealing themselves.</p>
    </section>
    <section id="charing-cross">
        <h3>Charing Cross Hotel</h3>
        <p>The sting at Charing Cross Hotel succeeds, apprehending the culprits behind the stolen plans.</p>
    </section>
    """.strip()

    chapters_js = "\n".join(
        [
            "const chapters = {",
            "    'baker': { bearing: 27, center: [-0.15591514, 51.51830379], zoom: 15.5, pitch: 20 },",
            "    'aldgate': { duration: 6000, center: [-0.07571203, 51.51424049], bearing: 150, zoom: 15, pitch: 0 },",
            "    'london-bridge': { bearing: 90, center: [-0.08533793, 51.50438536], zoom: 13, speed: 0.6, pitch: 40 },",
            "    'woolwich': { bearing: 90, center: [0.05991101, 51.48752939], zoom: 12.3 },",
            "    'gloucester': { bearing: 45, center: [-0.18335806, 51.49439521], zoom: 15.3, pitch: 20, speed: 0.5 },",
            "    'caulfield-gardens': { bearing: 180, center: [-0.19684993, 51.5033856], zoom: 12.3 },",
            "    'telegraph': { bearing: 90, center: [-0.10669358, 51.51433123], zoom: 17.3, pitch: 40 },",
            "    'charing-cross': { bearing: 90, center: [-0.12416858, 51.50779757], zoom: 14.3, pitch: 20 }",
            "};",
        ]
    )

    scroll_js = "\n".join(
        [
            "const story = document.createElement('div');",
            "story.id = 'features';",
            "story.className = 'maplibreum-story';",
            f"story.innerHTML = `{story_html}`;",
            "document.body.appendChild(story);",
            chapters_js,
            "window.onscroll = function () {",
            "    const chapterNames = Object.keys(chapters);",
            "    for (let i = 0; i < chapterNames.length; i++) {",
            "        const chapterName = chapterNames[i];",
            "        if (isElementOnScreen(chapterName)) {",
            "            setActiveChapter(chapterName);",
            "            break;",
            "        }",
            "    }",
            "};",
            "let activeChapterName = 'baker';",
            "function setActiveChapter(chapterName) {",
            "    if (chapterName === activeChapterName) return;",
            "    map.flyTo(chapters[chapterName]);",
            "    document.getElementById(chapterName).classList.add('active');",
            "    document.getElementById(activeChapterName).classList.remove('active');",
            "    activeChapterName = chapterName;",
            "}",
            "function isElementOnScreen(id) {",
            "    const element = document.getElementById(id);",
            "    const bounds = element.getBoundingClientRect();",
            "    return bounds.top < window.innerHeight && bounds.bottom > 0;",
            "}",
        ]
    )

    m.add_on_load_js(scroll_js)

    html = m.render()

    assert '"style": "https://tiles.openfreemap.org/styles/bright"' in html
    assert '"center": [-0.15591514, 51.51830379]' in html
    assert '"zoom": 15.5' in html
    assert '"bearing": 27' in html
    assert '"pitch": 45' in html
    assert "map.flyTo(chapters[chapterName]);" in html
    assert "window.onscroll" in html
