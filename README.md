# Markdown Link Extractor

A Python tool to extract all markdown links from files and subfolders, ignoring attachment links and providing source file and section information.
Used CLINE to play arround and build some tests a few code lines.

## Features

- **Multiple Link Format Support**: Handles both inline `[text](url)` and reference-style `[text][id]` links
- **Attachment Filtering**: Automatically ignores attachment links (relative paths, file:// links, etc.)
- **Section Tracking**: Tracks which markdown section/heading each link appears in
- **Source Information**: Records the source file, section, line number, and link text for each link
- **Recursive Scanning**: Scans directories recursively to find all .md files
- **Deduplication**: Removes duplicate links while preserving all source information
- **Sorted Output**: Outputs links alphabetically sorted with comprehensive source details
- **CLI Interface**: Easy-to-use command-line interface

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

Basic usage - scan a directory:
```bash
python3 mdlinks.py /path/to/markdown/files
```

Scan a single file:
```bash
python3 mdlinks.py single_file.md
```

Specify custom output file:
```bash
python3 mdlinks.py /path/to/markdown/files --output my_links.md
```

Non-recursive mode (only scan top-level .md files):
```bash
python3 mdlinks.py /path/to/markdown/files --no-recursive
```

Show help:
```bash
python3 mdlinks.py --help
```

### Direct Python Usage

```python
from src.markdown_link_extractor import MarkdownLinkExtractor

# Create extractor instance
extractor = MarkdownLinkExtractor()

# Extract links from a directory
links = extractor.extract_links_from_directory("/path/to/markdown/files")

# Generate output
extractor.generate_output(links, "output.md")

# Or extract from a single file
links = extractor.extract_links_from_file("single_file.md")
```

## Link Types Supported

### Inline Links
- Basic: `[text](https://example.com)`
- With title: `[text](https://example.com "Title")`
- Auto-links: `<https://example.com>`

### Reference Links
- Link definition: `[text][ref]` and `[ref]: https://example.com`
- Automatic references: `[text][]` and `[text]: https://example.com`

### Ignored Links (Attachments)
- Relative paths: `./file.md`, `../file.md`, `subfolder/file.md`
- File protocol: `file:///path/to/file`
- Absolute paths: `/absolute/path`, `C:\Windows\path` (Windows)
- Section links: `#section-name`

## Output Format

The generated markdown file includes:

- **Header**: Generation timestamp and summary statistics
- **Link Sections**: Each unique URL as a level-2 heading
- **Source Information**: For each link occurrence:
  - Source file path
  - Markdown section/heading
  - Link text (if available)
  - Line number (if available)

Example output:
```markdown
# Extracted Markdown Links

**Generated on:** Mon Dec 16 14:22:15 2024

**Total unique links:** 3
**Total link references:** 5

---

## https://www.python.org/

**Found in 2 location(s):**

- **data/test_links_1.md**
  - Section: External Links
  - Link text: "Python"
  - Line: 3

- **data/subfolder/test_links_2.md**
  - Section: Code Links
  - Link text: "Python Documentation"
  - Line: 15

---

## https://github.com/

**Found in 1 location(s):**

- **data/test_links_1.md**
  - Section: External Links
  - Link text: "GitHub"
  - Line: 4

---
```

## Project Structure

```
markdown_link_extractor/
├── src/
│   └── mdlinks.py  # Main implementation
├── data/
│   ├── test_links_1.md            # Sample test files
│   └── subfolder/
│       └── test_links_2.md
├── tests/                          # Unit tests (to be added)
├── requirements.txt                # Python dependencies
├── mdlinks.py      # CLI wrapper script
├── README.md                       # This file
└── TODO.md                         # Development progress
```

## Development

### Testing

Run the tool on the included test files:
```bash
python3 mdlinks.py data --output test_results.md
```

### Adding New Features

The tool is designed to be extensible:
- Add new link patterns to `LINK_PATTERNS` in the `MarkdownLinkExtractor` class
- Modify attachment filtering in `ATTACHMENT_PATTERNS`
- Customize output format in `generate_output()` method

## Requirements

- Python 3.6+
- Standard library modules: `re`, `os`, `pathlib`, `argparse`
- No external dependencies required for core functionality

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
