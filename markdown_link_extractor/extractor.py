import re
import json
from pathlib import Path
from typing import List, Dict, Optional

MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
INLINE_LINK_PATTERN = re.compile(r'<(https?://[^>]+)>')

def extract_links_from_text(text: str) -> List[Dict[str, Optional[str]]]:
    links = []
    for match in MD_LINK_PATTERN.finditer(text):
        name, url = match.groups()
        line = text[match.end():].split('\n', 1)[0].strip()
        description = None
        if line and not line.startswith('['):
            description = line.split('.')[0]
        links.append({'name': name.strip(), 'url': url.strip(), 'description': description})
    for match in INLINE_LINK_PATTERN.finditer(text):
        url = match.group(1)
        links.append({'name': url, 'url': url, 'description': None})
    return links

def extract_links_from_file(file_path: Path) -> List[Dict[str, Optional[str]]]:
    with file_path.open(encoding="utf-8") as f:
        text = f.read()
    return extract_links_from_text(text)

def extract_links_from_folder(folder_path: Path, recursive: bool = False) -> Dict[str, Dict]:
    folder_path = Path(folder_path)
    pattern = "**/*.md" if recursive else "*.md"
    results = {}
    for md_file in sorted(folder_path.glob(pattern)):
        links = extract_links_from_file(md_file)
        # Ensure 'name' can be safely lowercased even if it's None or missing
        links.sort(key=lambda l: (l.get("name") or "").lower())
        relative_folder = str(md_file.parent.relative_to(folder_path))
        results[md_file.stem] = {"folder": relative_folder or ".", "links": links}
    return results

def format_links_as_markdown(links_by_file: Dict[str, Dict]) -> str:
    output_lines = []
    for filename, data in links_by_file.items():
        folder_info = data["folder"]
        output_lines.append(f"## {filename}  _(Folder: {folder_info})_")
        for link in data["links"]:
            line = f"- [{link['name']}]({link['url']})"
            if link.get("description"):
                line += f"\n  - {link['description']}"
            output_lines.append(line)
        output_lines.append("")
    return "\n".join(output_lines)

def format_links_as_json(links_by_file: Dict[str, Dict]) -> str:
    return json.dumps(links_by_file, indent=2, ensure_ascii=False)
