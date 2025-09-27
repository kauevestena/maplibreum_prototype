from maplibreum import Map


def test_use_locally_generated_ideographs():
    m = Map(
        map_style="https://tiles.openfreemap.org/styles/bright",
        center=[120.3049, 31.4751],
        zoom=12,
        map_options={"localIdeographFontFamily": '"Apple LiSung", serif'},
    )

    assert m.additional_map_options["localIdeographFontFamily"] == '"Apple LiSung", serif'

    html = m.render()

    assert 'localIdeographFontFamily' in html
    assert '"center": [120.3049, 31.4751]' in html
    assert '"zoom": 12' in html
