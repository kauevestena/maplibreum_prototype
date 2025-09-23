from bs4 import BeautifulSoup
import requests
import os
import json
from pathlib import Path
from typing import Optional

base_folder = "misc/maplibre_examples"


base_url = "https://maplibre.org/maplibre-gl-js/docs/examples/"

# soup creation
response = requests.get(base_url)
soup = BeautifulSoup(response.content, "html.parser")

# Create the base folder if it doesn't exist
ouput_folder = os.path.join(base_folder, "pages")
os.makedirs(ouput_folder, exist_ok=True)

# get all "h2" elements:
h2_elements = soup.find_all("h2")

# iterate through all "h2" elements, and get the "a" child element, save in a dict, having the "id" attribute as key, and the full URL as value:
pages = {}
for h2 in h2_elements:
    a = h2.find("a")
    if a and h2.get("id"):
        # The id is on the h2 element, not the a element
        # Construct full URL by combining base_url with the relative href
        relative_url = a.get("href")
        full_url = base_url + relative_url if relative_url else None
        if full_url:
            pages[h2.get("id")] = full_url

# Print the results
print(f"Found {len(pages)} example pages:")
for page_id, href in list(pages.items())[:5]:  # Show first 5 examples
    print(f"  {page_id}: {href}")


status_path = os.path.join(base_folder, "status.json")
if os.path.exists(status_path):
    with open(status_path, "r", encoding="utf-8") as status_file:
        status_data = json.load(status_file)
else:
    status_data = {}


def normalise_script(page_id: str, existing: Optional[str]) -> Optional[str]:
    """Return a relative test path when a script exists on disk."""

    if existing:
        return existing

    candidate = Path("tests") / "test_examples" / f"test_{page_id.replace('-', '_')}.py"
    if candidate.exists():
        return str(candidate)
    return None


# iterating and saving each page
for page_id, href in pages.items():
    file_path = os.path.join(ouput_folder, f"{page_id}.html")

    existing_entry = status_data.get(page_id, {})
    inner = existing_entry.get(page_id, {})

    entry = {
        "url": href,
        "source_status": inner.get("source_status", False),
        "file_path": file_path,
        "task_status": inner.get("task_status", False),
        "script": normalise_script(page_id, inner.get("script")),
    }

    print(f"Fetching {page_id} from {href}...")
    response = requests.get(href)
    if response.status_code == 200:

        # create a soup object to parse the HTML content
        example_soup = BeautifulSoup(response.content, "html.parser")

        # extract the <code class="md-code__content" tabindex="0"> element
        code_element = example_soup.find(
            "code", class_="md-code__content", tabindex="0"
        )
        if code_element:
            content = code_element.get_text(strip=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Saved to {file_path}")

            entry["source_status"] = True
        else:
            print(f"  No <code> element found in {href}")
            entry["source_status"] = False
    else:
        print(f"  Failed to fetch {href}: Status code {response.status_code}")

    status_data[page_id] = {page_id: entry}

# Save the pages dictionary to a JSON file
output_file = os.path.join(base_folder, "status.json")
sorted_status = {key: status_data[key] for key in sorted(status_data)}
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sorted_status, f, indent=2)
    f.write("\n")

print(f"\nSaved {len(pages)} example URLs to {output_file}")
