# Markdown Link Extractor - Task Progress

## Project Goals
Create a Python project to extract all markdown links from files in folders/subfolders, ignore attachment links, and output sorted, unique links with source file and section information.

## Implementation Checklist

### Phase 1: Project Setup
- [x] Create project structure (src, tests, data directories)
- [ ] Create requirements.txt file
- [ ] Create setup.py or pyproject.toml
- [ ] Initialize git repository (if needed)

### Phase 2: Core Link Extraction
- [ ] Create main markdown parser class
- [ ] Implement regex patterns for different markdown link formats
- [ ] Add section/heading tracking functionality
- [ ] Implement attachment link filtering
- [ ] Add source file and section information tracking

### Phase 3: File Processing
- [ ] Implement recursive folder traversal for .md files
- [ ] Add file reading and content parsing
- [ ] Implement link deduplication logic
- [ ] Add sorting functionality

### Phase 4: Output Generation
- [ ] Create markdown output formatter
- [ ] Implement structured output with source information
- [ ] Add command-line interface
- [ ] Create configuration options

### Phase 5: Testing & Validation
- [ ] Create sample test markdown files
- [ ] Write unit tests for core functionality
- [ ] Test edge cases and various link formats
- [ ] Validate output format

### Phase 6: Documentation & Examples
- [ ] Create README.md with usage instructions
- [ ] Add code documentation
- [ ] Create example output
- [ ] Add usage examples

## Key Features to Implement
- Support for various markdown link formats: `[text](url)`, `[text](url "title")`, etc.
- Section tracking (headings)
- Attachment link filtering (links starting with ./, ../, or file://)
- Source file and section information for each link
- Sorted and deduplicated output
- CLI interface for easy usage
