"""Data sources for maplibreum."""

from textwrap import dedent


class RESTDataSource:
    """Represents a REST API data source."""

    def __init__(self, url: str):
        self.url = url

    def to_js(self) -> str:
        """Generates the JavaScript code to fetch data from the REST API.

        Returns:
            str: The JavaScript code to fetch the data.
        """
        js_code = dedent(f"""
            fetch('{self.url}')
                .then(response => response.json())
        """)
        return js_code
