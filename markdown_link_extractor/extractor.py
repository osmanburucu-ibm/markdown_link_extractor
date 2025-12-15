import re
import json
from pathlib import Path
from typing import List, Dict, Optional

# Regex patterns for Markdown links
URL_SCHEMA = r'(?:[a-zA-Z][a-zA-Z0-9+]*://|[./]+/?|#)'  # schemes like https://, ftp://, relative ./, /, #anchor
URL_SCHEMA_PROTOCOL = r'[a-zA-Z][a-zA-Z0-9+]*://'  # only protocols for bare URLs to avoid partial matches
MD_INLINE_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\((' + URL_SCHEMA + r'[^"\s]*)(?:\s*"([^"]*)")?\)')  # [name](url) or [name](url "title")
MD_REF_LINK_PATTERN = re.compile(r'\[([^\]]+)\](?:\s*\[([^\]]*)\])?')  # [text] or [text][ref]
REF_DEF_PATTERN = re.compile(r'^[ \t]*\[([^\]]+)\]:\s*([^ \t\n]+)(?:\s*"([^"]*)")?')  # [ref]: url or [ref]: url "title"
INLINE_LINK_PATTERN = re.compile(r'<(' + URL_SCHEMA + r'[^>\s]+)>')  # <url> with any scheme
BARE_URL_PATTERN = re.compile(r'(?<![\w(\<\>)])(' + URL_SCHEMA_PROTOCOL + r'[^\s)>\]]*)')  # bare URLs with protocols, not after word

# Strings or patterns to ignore in URLs or names
IGNORE_PATTERNS = ["@attachment"]

def should_ignore_link(name: str, url: str) -> bool:
    """Check whether a link should be ignored based on its name or URL."""
    lower_name = name.lower()
    lower_url = url.lower()
    return any(p in lower_name or p in lower_url for p in IGNORE_PATTERNS)


def extract_links_from_text(text: str) -> List[Dict[str, Optional[str]]]:
    """
    Extract Markdown-style hyperlinks, images, inline <URL>, and bare URLs from text.
    Filters out links containing ignore patterns.
    """
    links = []

    # First pass: collect reference definitions
    ref_defs = {}
    for line in text.splitlines():
        match = REF_DEF_PATTERN.match(line)
        if match:
            ref, url, title = match.groups()
            ref_defs[ref] = {'url': url.strip(), 'title': (title or "").strip() or None}

    # Now extract all link types
    lines = text.splitlines()

    # Pattern for inline links and images: ([name](url "title") or ![alt](url)
    INLINE_PATTERN = re.compile(r'(!?)\[([^\]]*)\]\((' + URL_SCHEMA + r'[^"\s]*)(?:\s*"([^"]*)")?\)')
    # For reference links: [text] or [text][ref]
    REF_PATTERN = re.compile(r'(!?)\[([^\]]*)\](?:\s*\[([^\]]*)\])?')

    all_matches = []  # list of (start, end, type, groups)

    # Find all inline/link matches
    for match in INLINE_PATTERN.finditer(text):
        is_image, name, url, title = match.groups()
        start = match.start()
        all_matches.append((start, match.end(), 'inline', (is_image, name, url, title)))

    # Find all ref link matches, but exclude those inside inline if already matched
    inline_ranges = {(s,e) for s,e,t,g in all_matches if t=='inline'}
    for match in REF_PATTERN.finditer(text):
        start = match.start()
        end = match.end()
        if any(start >= s and end <= e for s,e in inline_ranges):
            continue  # already captured as inline
        if end < len(text) and text[end] == ':':
            continue  # likely a reference definition, skip
        is_image, text_part, ref = match.groups()
        all_matches.append((start, end, 'ref', (is_image, text_part, ref)))

    # Sort by start position
    all_matches.sort()

    for start, end, link_type, groups in all_matches:
        if link_type == 'inline':
            is_image, name, url, title = groups
            name = name or ""  # for images, alt text can be empty
            url = url.strip()
            if should_ignore_link(name, url):
                continue
            # Determine description from following text if no title
            following_lines = text[end:].split('\n', 2)
            description = title  # prefer title over following
            if not description and len(following_lines) > 0:
                line = following_lines[0].strip()
                if line and not line.startswith('['):
                    description = line.split('.')[0].strip()
            links.append({'name': name.strip(), 'url': url, 'description': description, 'type': 'image' if is_image else 'link'})
        elif link_type == 'ref':
            is_image, text_part, ref = groups
            ref = ref or text_part  # default ref to text if not specified
            def_info = ref_defs.get(ref)
            if not def_info:
                continue  # no definition found, skip
            url = def_info['url']
            title = def_info.get('title')
            if should_ignore_link(text_part, url):
                continue
            description = title  # use title from def
            if not description:
                following_lines = text[end:].split('\n', 2)
                if len(following_lines) > 0:
                    line = following_lines[0].strip()
                    if line and not line.startswith('['):
                        description = line.split('.')[0].strip()
            links.append({'name': text_part.strip(), 'url': url, 'description': description, 'type': 'image' if is_image else 'link'})

    # Inline angle-bracket links <url>
    for match in INLINE_LINK_PATTERN.finditer(text):
        url = match.group(1).strip()
        if should_ignore_link(url, url):
            continue
        # Avoid duplicates
        if not any(l["url"] == url for l in links):
            links.append({'name': url, 'url': url, 'description': None, 'type': 'link'})

    # Bare URLs
    for match in BARE_URL_PATTERN.finditer(text):
        url = match.group(1).strip()
        if should_ignore_link(url, url):
            continue
        # Avoid duplicates
        if not any(l["url"] == url for l in links):
            links.append({'name': url, 'url': url, 'description': None, 'type': 'link'})

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
