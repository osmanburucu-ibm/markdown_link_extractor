import re
import json
from pathlib import Path
from typing import List, Dict, Optional

# Regex patterns for Markdown links
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
INLINE_LINK_PATTERN = re.compile(r'<(https?://[^>]+)>')
BARE_URL_PATTERN = re.compile(r'(?<!\()(?<!<)(https?://[^\s)>\]]+)')  # bare URLs not in ()

# Strings or patterns to ignore in URLs or names
IGNORE_PATTERNS = ["@attachment"]

def should_ignore_link(name: str, url: str) -> bool:
    """Check whether a link should be ignored based on its name or URL."""
    lower_name = name.lower()
    lower_url = url.lower()
    return any(p in lower_name or p in lower_url for p in IGNORE_PATTERNS)


def extract_links_from_text(text: str) -> List[Dict[str, Optional[str]]]:
    """
    Extract Markdown-style, inline <URL>, and bare URLs from text.
    Filters out links containing ignore patterns.
    """
    links = []

    # Standard Markdown links [name](url)
    for match in MD_LINK_PATTERN.finditer(text):
        name, url = match.groups()
        if should_ignore_link(name, url):
            continue
        line = text[match.end():].split('\n', 1)[0].strip()
        description = None
        if line and not line.startswith('['):
            description = line.split('.')[0]
        links.append({'name': name.strip(), 'url': url.strip(), 'description': description})

    # Inline angle-bracket links <https://example.com>
    for match in INLINE_LINK_PATTERN.finditer(text):
        url = match.group(1)
        if should_ignore_link(url, url):
            continue
        links.append({'name': url, 'url': url, 'description': None})

    # Bare URLs (https://example.com)
    for match in BARE_URL_PATTERN.finditer(text):
        url = match.group(1)
        if should_ignore_link(url, url):
            continue
        # Avoid duplicates if already captured
        if not any(l["url"] == url for l in links):
            links.append({'name': url, 'url': url, 'description': None})

    return links


def extract_links_from_file(file_path: Path) -> List[Dict[str, Optional[str]]]:
    """Extract links from a single Markdown file."""
    with file_path.open(encoding="utf-8") as f:
        text = f.read()
    return extract_links_from_text(text)


def extract_links_from_folder(folder_path: Path, recursive: bool = False) -> Dict[str, Dict]:
    """
    Extract and organize links from Markdown files in the folder.

    Args:
        folder_path (Path): root folder
        recursive (bool): include subfolders if True

    Returns:
        dict: {filename: {"folder": <relative_path>, "links": [list of links]}}
    """
    folder_path = Path(folder_path)
    pattern = "**/*.md" if recursive else "*.md"
    results = {}

    for md_file in sorted(folder_path.glob(pattern)):
        links = extract_links_from_file(md_file)
        links.sort(key=lambda l: (l.get("name") or "").lower())
        relative_folder = str(md_file.parent.relative_to(folder_path))
        results[md_file.stem] = {"folder": relative_folder or ".", "links": links}

    return results


def format_links_as_markdown(links_by_file: Dict[str, Dict]) -> str:
    """Format extracted links as Markdown text."""
    output_lines = []
    for filename, data in links_by_file.items():
        folder_info = data["folder"]
        output_lines.append(f"## {filename}  _(Folder: {folder_info})_")
        for link in data["links"]:
            line = f"- [{link['name']}]({link['url']})"
            if link.get("description"):
                line += f"\n  - {link['description']}"
            output_lines.append(line)
        output_lines.append("")  # blank line
    return "\n".join(output_lines)


def format_links_as_json(links_by_file: Dict[str, Dict]) -> str:
    """Format extracted links as JSON."""
    return json.dumps(links_by_file, indent=2, ensure_ascii=False)
