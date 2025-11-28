import sys
from pathlib import Path
from .extractor import (
    extract_links_from_folder,
    format_links_as_markdown,
    format_links_as_json,
)

def main():
    """
    Usage:
        md-links <path_to_folder> [output_file] [--json] [--recursive | -r]
    """
    if len(sys.argv) < 2:
        print("Usage: md-links <path_to_folder> [output_file] [--json] [--recursive | -r]")
        sys.exit(1)

    folder_path = Path(sys.argv[1])
    if not folder_path.is_dir():
        print(f"Error: {folder_path} is not a valid directory.")
        sys.exit(1)

    output_file = None
    json_output = False
    recursive = False
    for arg in sys.argv[2:]:
        if arg in ("--json", "-j"):
            json_output = True
        elif arg in ("--recursive", "-r"):
            recursive = True
        elif not arg.startswith("--"):
            output_file = Path(arg)

    results = extract_links_from_folder(folder_path, recursive=recursive)
    if json_output or (output_file and output_file.suffix.lower() == ".json"):
        output_text = format_links_as_json(results)
    else:
        output_text = format_links_as_markdown(results)

    if output_file:
        output_file.write_text(output_text, encoding="utf-8")
        print(f"✅ Output written to: {output_file}")
    else:
        print(output_text)
