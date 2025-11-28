import json
from pathlib import Path
import pytest
from markdown_link_extractor import extractor

SAMPLE_MD = """
# Example Links
[Python Docs](https://docs.python.org) Official Python documentation.
[GitHub](https://github.com)
<https://example.com>
"""

def test_extract_links_from_text_basic():
    links = extractor.extract_links_from_text(SAMPLE_MD)
    assert len(links) == 3
    names = [l["name"] for l in links]
    assert "Python Docs" in names
    assert "GitHub" in names
    assert "https://example.com" in names

def test_extract_links_from_file(tmp_path):
    md_file = tmp_path / "sample.md"
    md_file.write_text(SAMPLE_MD, encoding="utf-8")
    links = extractor.extract_links_from_file(md_file)
    assert len(links) == 3

def test_extract_links_from_folder_non_recursive(tmp_path):
    md_file = tmp_path / "sample.md"
    md_file.write_text(SAMPLE_MD, encoding="utf-8")
    results = extractor.extract_links_from_folder(tmp_path)
    assert "sample" in results
    assert results["sample"]["folder"] == "."

def test_extract_links_from_folder_recursive(tmp_path):
    subdir = tmp_path / "sub"
    subdir.mkdir()
    md_file = subdir / "nested.md"
    md_file.write_text(SAMPLE_MD, encoding="utf-8")
    results = extractor.extract_links_from_folder(tmp_path, recursive=True)
    assert "nested" in results
    assert results["nested"]["folder"] == "sub"

def test_format_links_as_markdown(tmp_path):
    md_file = tmp_path / "sample.md"
    md_file.write_text(SAMPLE_MD, encoding="utf-8")
    results = extractor.extract_links_from_folder(tmp_path)
    md_out = extractor.format_links_as_markdown(results)
    assert "## sample" in md_out
    assert "[Python Docs]" in md_out

def test_format_links_as_json(tmp_path):
    md_file = tmp_path / "sample.md"
    md_file.write_text(SAMPLE_MD, encoding="utf-8")
    results = extractor.extract_links_from_folder(tmp_path)
    json_out = extractor.format_links_as_json(results)
    data = json.loads(json_out)
    assert "sample" in data
    assert isinstance(data["sample"]["links"], list)
