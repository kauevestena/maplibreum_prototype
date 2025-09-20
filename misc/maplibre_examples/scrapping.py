from bs4 import BeautifulSoup
import requests
import os
import json

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


control_dict = {}
# iterating and saving each page
for page_id, href in pages.items():
    file_path = os.path.join(ouput_folder, f"{page_id}.html")

    control_dict[page_id] = {
        page_id: {
            "url": href,
            "source_status": False,
            "file_path": file_path,
            "task_status": False,
        }
    }

    print(f"Fetching {page_id} from {href}...")
    response = requests.get(href)
    if response.status_code == 200:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"  Saved to {file_path}")

        control_dict[page_id][page_id]["source_status"] = True
    else:
        print(f"  Failed to fetch {href}: Status code {response.status_code}")

# Save the pages dictionary to a JSON file
output_file = os.path.join(base_folder, "status.json")
with open(output_file, "w") as f:
    json.dump(control_dict, f, indent=2)

print(f"\nSaved {len(pages)} example URLs to {output_file}")
