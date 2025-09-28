from bs4 import BeautifulSoup
import requests
import os
import json
import logging
import time
from pathlib import Path
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

base_folder = "misc/maplibre_examples"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.3
RATE_LIMIT_DELAY = 0.1  # seconds between requests


def create_robust_session() -> requests.Session:
    """Create a requests session with retry strategy and proper configuration."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
        raise_on_status=False  # Don't raise exception on bad status codes
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set user agent and headers
    session.headers.update({
        'User-Agent': 'MapLibreum Examples Scraper 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    return session


def safe_http_request(session: requests.Session, url: str, description: str = "") -> Optional[requests.Response]:
    """Make a safe HTTP request with proper error handling.
    
    Args:
        session: Configured requests session
        url: URL to fetch
        description: Description for logging purposes
        
    Returns:
        Response object if successful, None otherwise
    """
    if not url or not isinstance(url, str):
        logger.error(f"Invalid URL provided: {url}")
        return None
        
    try:
        logger.info(f"Fetching {description}: {url}")
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            logger.debug(f"Successfully fetched {url}")
            return response
        elif response.status_code == 404:
            logger.warning(f"Resource not found (404): {url}")
        elif response.status_code == 403:
            logger.warning(f"Access forbidden (403): {url}")
        elif response.status_code == 429:
            logger.warning(f"Rate limited (429): {url}")
        else:
            logger.warning(f"HTTP {response.status_code} for {url}")
            
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout after {REQUEST_TIMEOUT}s: {url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        
    return None


base_url = "https://maplibre.org/maplibre-gl-js/docs/examples/"

# Create robust session
session = create_robust_session()

# soup creation
response = safe_http_request(session, base_url, "main examples page")
if not response:
    logger.error(f"Failed to fetch main examples page: {base_url}")
    exit(1)

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
logger.info(f"Found {len(pages)} example pages")
for page_id, href in list(pages.items())[:5]:  # Show first 5 examples
    logger.info(f"  {page_id}: {href}")


status_path = os.path.join(base_folder, "status.json")
try:
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as status_file:
            status_data = json.load(status_file)
        logger.info(f"Loaded existing status from {status_path}")
    else:
        status_data = {}
        logger.info("No existing status file found, starting fresh")
except (json.JSONDecodeError, IOError) as e:
    logger.error(f"Failed to load status file {status_path}: {e}")
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

    # Rate limiting
    time.sleep(RATE_LIMIT_DELAY)

    logger.info(f"Processing {page_id} from {href}")
    response = safe_http_request(session, href, f"example page {page_id}")
    
    if response:
        try:
            # create a soup object to parse the HTML content
            example_soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"Failed to parse HTML for {page_id}: {e}")
            status_data[page_id] = entry
            continue

        # Try multiple approaches to find the code
        maplibre_script = None

        # Approach 1: Look for code in <script> tags
        script_elements = example_soup.find_all("script")

        for script in script_elements:
            try:
                script_content = script.get_text(strip=False)
                script_src = script.get("src", "")

                if (
                    not script_src
                    and script_content
                    and any(
                        pattern in script_content
                        for pattern in [
                            "maplibregl.Map",
                            "new maplibregl",
                            "maplibregl.",
                            "Map({",
                            "new Map(",
                        ]
                    )
                ):
                    maplibre_script = script_content
                    logger.debug(f"    Found MapLibre script in script tag for {page_id}")
                    break
            except Exception as e:
                logger.warning(f"Error processing script tag for {page_id}: {e}")
                continue

        # Approach 2: Look for code in <pre> or <code> elements
        if not maplibre_script:
            try:
                code_elements = example_soup.find_all(["pre", "code"])

                for code_elem in code_elements:
                    code_content = code_elem.get_text(strip=False)
                    if code_content and any(
                        pattern in code_content
                        for pattern in [
                            "maplibregl.Map",
                            "new maplibregl",
                            "maplibregl.",
                            "Map({",
                            "new Map(",
                        ]
                    ):
                        maplibre_script = code_content
                        logger.debug(f"    Found MapLibre script in code element for {page_id}")
                        break
            except Exception as e:
                logger.warning(f"Error processing code elements for {page_id}: {e}")

        # Approach 3: Look for code in any element that might contain "const map = "
        if not maplibre_script:
            try:
                all_text = example_soup.get_text()
                if "const map = " in all_text or "maplibregl.Map" in all_text:
                    # Try to extract script blocks from the formatted content
                    lines = all_text.split("\n")
                    script_lines = []
                    in_script = False

                    for line in lines:
                        if any(
                            pattern in line
                            for pattern in [
                                "const map = ",
                                "new maplibregl.Map",
                                "maplibregl.Map",
                            ]
                        ):
                            in_script = True
                            script_lines.append(line)
                        elif in_script:
                            if (
                                line.strip()
                                and not line.startswith(" ")
                                and not line.startswith("\t")
                            ):
                                break
                            script_lines.append(line)

                    if script_lines:
                        maplibre_script = "\n".join(script_lines)
                        logger.debug(f"    Extracted script from page text for {page_id}")
            except Exception as e:
                logger.warning(f"Error extracting script from page text for {page_id}: {e}")

        if maplibre_script:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(maplibre_script)
                logger.info(f"  Saved JavaScript to {file_path}")
                entry["source_status"] = True
            except IOError as e:
                logger.error(f"Failed to save JavaScript for {page_id}: {e}")
                entry["source_status"] = False
        else:
            logger.warning(f"  No MapLibre script found in {href}")
            entry["source_status"] = False
    else:
        logger.error(f"  Failed to fetch {href}")

    status_data[page_id] = entry

# Save the pages dictionary to a JSON file
output_file = os.path.join(base_folder, "status.json")
sorted_status = {key: status_data[key] for key in sorted(status_data)}

try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_status, f, indent=2)
        f.write("\n")
    logger.info(f"Successfully saved {len(pages)} example URLs to {output_file}")
except IOError as e:
    logger.error(f"Failed to save status file {output_file}: {e}")

# Summary statistics
total_pages = len(pages)
successful_fetches = sum(1 for entry in status_data.values() if entry.get("source_status", False))
logger.info(f"Summary: {successful_fetches}/{total_pages} pages processed successfully")
