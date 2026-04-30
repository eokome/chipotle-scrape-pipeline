import os
import re
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")
RAW_DIR = Path("knowledge/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# --- Step 01: Search + scrape with Firecrawl ---

api_url = "https://api.firecrawl.dev/v2/search"

headers = {
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "query": "Chipotle investor relations press releases",
    "limit": 5,
    "scrapeOptions": {"formats": ["markdown"]}
}

response = requests.post(api_url, headers=headers, json=payload)
response.raise_for_status()

data = response.json() # convert response to JSON
results = data["data"]["web"] # get the results from the response
print(f"Firecrawl returned {len(results)} results")

for i, r in enumerate(results, start=1):
    print(f"  - {r['title']}")
    print(f"    {r['url']}")
    print(f"    markdown length: {len(r.get('markdown') or '')} chars")

    title_slug = re.sub(r"[^a-zA-Z0-9]+", "-", r["title"].lower()).strip("-")
    filename = f"{i:02d}-{title_slug}.md"
    filepath = RAW_DIR / filename
    content = f"---\nurl: {r['url']}\ntitle: {r['title']}\n---\n\n{r.get('markdown') or ''}"
    label = "[overwrite]" if filepath.exists() else "[saved]"
    filepath.write_text(content, encoding="utf-8")
    print(f"  {label} {filepath}")