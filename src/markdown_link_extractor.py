"""
Markdown Link Extractor

A tool to extract all markdown links from files and subfolders, 
ignoring attachment links and providing source file and section information.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class LinkInfo:
    """Information about a found markdown link"""
    url: str
    source_file: str
    section: str
    link_text: Optional[str] = None
    line_number: Optional[int] = None
    
    def __hash__(self):
        return hash((self.url, self.source_file, self.section))


class MarkdownLinkExtractor:
    """Extracts markdown links from files and tracks their sources"""
    
    # Regex patterns for different markdown link formats
    LINK_PATTERNS = [
        # Basic markdown links: [text](url)
        r'\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',
        # Reference-style links: [text][id] -> [id]: url
        r'\[([^\]]*)\]\[([^\]]+)\]',
        r'\[([^\]]+)\]:\s*([^\s]+)(?:\s+"[^"]*")?',
    ]
    
    # Attachment link patterns to ignore
    ATTACHMENT_PATTERNS = [
        r'^\.\.?/',
        r'^file://',
        r'^[a-zA-Z]:\\',  # Windows absolute paths
        r'^\/',  # Absolute Unix paths
    ]
    
    def __init__(self):
        self.links: List[LinkInfo] = []
        self.attachment_patterns = [re.compile(pattern) for pattern in self.ATTACHMENT_PATTERNS]
    
    def is_attachment_link(self, url: str) -> bool:
        """Check if a URL is an attachment link that should be ignored"""
        url = url.strip()
        
        # Check for @attachment in the URL
        if '@attachment' in url.lower():
            return True
        
        # Check against patterns
        for pattern in self.attachment_patterns:
            if pattern.match(url):
                return True
        return False
    
    def extract_section_from_headings(self, content: str, current_line: int) -> str:
        """Find the nearest heading above the current line"""
        lines = content.split('\n')
        current_section = "Document"
        
        for i in range(current_line - 1, -1, -1):
            line = lines[i].strip()
            # Match various heading formats
            if line.startswith('#'):
                # Extract heading text, removing # symbols and formatting
                heading_text = re.sub(r'^#+\s*', '', line)
                heading_text = re.sub(r'\s*#*$', '', heading_text)
                current_section = heading_text
                break
        
        return current_section
    
    def extract_links_from_content(self, content: str, source_file: str) -> List[LinkInfo]:
        """Extract all markdown links from file content"""
        links = []
        lines = content.split('\n')
        
        # First pass: extract basic markdown links [text](url)
        for line_num, line in enumerate(lines, 1):
            # Basic markdown links
            matches = re.finditer(self.LINK_PATTERNS[0], line)
            for match in matches:
                link_text = match.group(1).strip()
                url = match.group(2).strip()
                
                if not self.is_attachment_link(url):
                    section = self.extract_section_from_headings(content, line_num)
                    links.append(LinkInfo(
                        url=url,
                        source_file=source_file,
                        section=section,
                        link_text=link_text,
                        line_number=line_num
                    ))
        
        # Second pass: handle reference-style links
        # First collect all reference definitions
        references = {}
        for line_num, line in enumerate(lines, 1):
            match = re.match(self.LINK_PATTERNS[2], line)
            if match:
                ref_id = match.group(1).strip()
                url = match.group(2).strip()
                references[ref_id] = url
        
        # Then find reference-style links and match them
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(self.LINK_PATTERNS[1], line)
            for match in matches:
                link_text = match.group(1).strip()
                ref_id = match.group(2).strip()
                
                if ref_id in references and not self.is_attachment_link(references[ref_id]):
                    url = references[ref_id]
                    section = self.extract_section_from_headings(content, line_num)
                    links.append(LinkInfo(
                        url=url,
                        source_file=source_file,
                        section=section,
                        link_text=link_text,
                        line_number=line_num
                    ))
        
        # Third pass: handle auto-links in angle brackets <url">
        for line_num, line in enumerate(lines, 1):
            # Handle HTTP/HTTPS URLs
            matches = re.finditer(r'<(https?://[^>\s]+)>', line)
            for match in matches:
                url = match.group(1).strip()
                if not self.is_attachment_link(url):
                    section = self.extract_section_from_headings(content, line_num)
                    links.append(LinkInfo(
                        url=url,
                        source_file=source_file,
                        section=section,
                        link_text=url,  # For auto-links, URL is the text
                        line_number=line_num
                    ))
            
            # Handle FTP URLs
            matches = re.finditer(r'<(ftp://[^>\s]+)>', line)
            for match in matches:
                url = match.group(1).strip()
                if not self.is_attachment_link(url):
                    section = self.extract_section_from_headings(content, line_num)
                    links.append(LinkInfo(
                        url=url,
                        source_file=source_file,
                        section=section,
                        link_text=url,
                        line_number=line_num
                    ))
            
            # Handle mailto URLs
            matches = re.finditer(r'<(mailto:[^>\s]+)>', line)
            for match in matches:
                url = match.group(1).strip()
                if not self.is_attachment_link(url):
                    section = self.extract_section_from_headings(content, line_num)
                    links.append(LinkInfo(
                        url=url,
                        source_file=source_file,
                        section=section,
                        link_text=url,
                        line_number=line_num
                    ))
        
        return links
    
    def extract_links_from_file(self, file_path: str) -> List[LinkInfo]:
        """Extract all markdown links from a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.extract_links_from_content(content, file_path)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
    
    def extract_links_from_directory(self, directory_path: str, recursive: bool = True) -> List[LinkInfo]:
        """Extract all markdown links from all .md files in a directory"""
        directory = Path(directory_path)
        all_links = []
        
        # Find all markdown files
        pattern = "**/*.md" if recursive else "*.md"
        markdown_files = list(directory.glob(pattern))
        
        print(f"Found {len(markdown_files)} markdown files to process")
        
        for md_file in markdown_files:
            print(f"Processing: {md_file}")
            links = self.extract_links_from_file(str(md_file))
            all_links.extend(links)
        
        return all_links
    
    def deduplicate_and_sort_links(self, links: List[LinkInfo]) -> Dict[str, List[LinkInfo]]:
        """Remove duplicate links and group by URL, then sort"""
        link_groups = defaultdict(list)
        
        # Group links by URL
        for link in links:
            link_groups[link.url].append(link)
        
        # Sort each group by source file, then section
        for url, url_links in link_groups.items():
            url_links.sort(key=lambda x: (x.source_file, x.section, x.line_number or 0))
        
        # Sort URLs alphabetically
        sorted_links = {}
        for url in sorted(link_groups.keys()):
            sorted_links[url] = link_groups[url]
        
        return sorted_links
    
    def generate_output(self, links: List[LinkInfo], output_file: str) -> None:
        """Generate markdown output with all links, sorted and with source information"""
        if not links:
            print("No links found to output")
            return
        
        # Deduplicate and sort links
        link_groups = self.deduplicate_and_sort_links(links)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Extracted Markdown Links\n\n")
            f.write(f"**Generated on:** {os.popen('date').read().strip()}\n\n")
            f.write(f"**Total unique links:** {len(link_groups)}\n")
            f.write(f"**Total link references:** {sum(len(group) for group in link_groups.values())}\n\n")
            f.write("---\n\n")
            
            for url, url_links in link_groups.items():
                # Create a readable link name from URL
                link_name = self._generate_link_name(url)
                f.write(f"## [{link_name}]({url})\n\n")
                f.write(f"**URL:** `{url}`\n\n")
                f.write(f"**Found in {len(url_links)} location(s):**\n\n")
                
                for link in url_links:
                    f.write(f"- **{link.source_file}**\n")
                    if link.section != "Document":
                        f.write(f"  - Section: {link.section}\n")
                    if link.link_text and link.link_text != url:
                        f.write(f"  - Link text: \"{link.link_text}\"\n")
                    if link.line_number:
                        f.write(f"  - Line: {link.line_number}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        print(f"Output written to {output_file}")
    
    def _generate_link_name(self, url: str) -> str:
        """Generate a readable name from URL"""
        # Remove protocol and common prefixes
        url_clean = re.sub(r'^https?://', '', url)
        url_clean = re.sub(r'^www\.', '', url_clean)
        
        # Take the first part before any path
        parts = url_clean.split('/')
        domain = parts[0]
        
        # Capitalize domain for readability
        domain_parts = domain.split('.')
        main_domain = domain_parts[0].capitalize()
        
        return main_domain


def main():
    """Main function to run the markdown link extractor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract markdown links from files and directories")
    parser.add_argument("path", help="Path to directory or file to scan")
    parser.add_argument("-o", "--output", default="extracted_links.md", 
                       help="Output file name (default: extracted_links.md)")
    parser.add_argument("--no-recursive", action="store_true", 
                       help="Don't scan subdirectories recursively")
    
    args = parser.parse_args()
    
    extractor = MarkdownLinkExtractor()
    
    if os.path.isfile(args.path):
        print(f"Processing single file: {args.path}")
        links = extractor.extract_links_from_file(args.path)
    elif os.path.isdir(args.path):
        print(f"Processing directory: {args.path}")
        links = extractor.extract_links_from_directory(args.path, not args.no_recursive)
    else:
        print(f"Error: Path '{args.path}' is not a valid file or directory")
        return
    
    if links:
        extractor.generate_output(links, args.output)
        print(f"Found {len(set(link.url for link in links))} unique links")
        print(f"Total link references: {len(links)}")
    else:
        print("No links found")


if __name__ == "__main__":
    main()
