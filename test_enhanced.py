from pathlib import Path
from markdown_link_extractor.extractor import extract_links_from_file
import json

links = extract_links_from_file(Path('test_sample.md'))
for link in links:
    print(link)
print()
print(json.dumps(links, indent=2))
