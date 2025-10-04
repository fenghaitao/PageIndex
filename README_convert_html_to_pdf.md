# HTML to PDF Converter using pwhtmltopdf

This script demonstrates how to convert local HTML files to PDF using the `pwhtmltopdf` library, which leverages Playwright for high-fidelity PDF generation.

## Features

- Convert individual HTML files to PDF
- Convert all HTML files in a directory to PDF
- **Recursively merge linked HTML files with multiple hierarchy levels into a single PDF**
- Automatically discovers and follows links through any depth of HTML file hierarchies
- Maintains internal navigation links between merged documents
- Customizable PDF options (page size, margins, etc.)
- Support for CSS styling in the generated PDF
- Asynchronous processing for better performance
- Prevents infinite loops with configurable maximum recursion depth

## Prerequisites

The `pwhtmltopdf` library should already be installed in your environment. It requires Playwright to function properly.

Additionally, install the Chromium browser for Playwright:

```bash
playwright install chromium
```

## Usage

### Convert a single HTML file to PDF:

```bash
python convert_html_to_pdf.py input.html output.pdf
```

### Convert all HTML files in a directory:

```bash
python convert_html_to_pdf.py /path/to/html/files /path/to/output/directory
```

### Create a sample HTML file for testing:

```bash
python convert_html_to_pdf.py --create-sample sample.html
```

### Merge all linked HTML files from an index file into a single PDF:

```bash
python convert_html_to_pdf.py --merge-linked index.html merged_output.pdf
```

The `--merge-linked` option now supports **recursive hierarchy traversal**. It will:
- Start from the index HTML file
- Follow all links to other HTML files
- Recursively process each linked HTML file, following their links as well
- Continue until all connected HTML files are discovered (up to max depth)
- Merge all files into a single PDF while maintaining internal navigation

#### Advanced options for merge-linked:

```bash
# Specify maximum recursion depth (default: 10)
python convert_html_to_pdf.py --merge-linked index.html output.pdf --max-depth=5
```

## Script Options

The script accepts different parameters based on the first argument:

1. **File conversion**: When the first argument is a path to an HTML file
   - Second argument (optional): output PDF file path

2. **Directory conversion**: When the first argument is a directory
   - Second argument (optional): output directory for PDF files

3. **Create sample**: When the first argument is `--create-sample`
   - Second argument: path where to create the sample HTML file

4. **Merge linked**: When the first argument is `--merge-linked`
   - Second argument: index HTML file containing links to other HTML files
   - Third argument (optional): output PDF file path
   - `--max-depth=N` (optional): Maximum recursion depth for following links (default: 10)

## Customization

You can customize PDF generation by modifying the `pdf_options` dictionary in the script:

- `format`: Page format (e.g., 'A4', 'A3', 'Letter', etc.)
- `print_background`: Whether to print background graphics
- `margin`: Page margins (top, bottom, left, right)
- `scale`: Scale of the webpage rendering
- `display_header_footer`: Display header and footer
- `landscape`: Paper orientation

## Example

The script includes a `create_sample_html()` function which generates a sample HTML file with various elements (text, tables, CSS styling) to demonstrate the conversion capabilities.

## Multi-Level Hierarchy Example

The enhanced `--merge-linked` option can handle complex HTML documentation with multiple levels:

```
index.html
├─ chapter1.html
│  ├─ section1-1.html
│  │  ├─ subsection1-1-1.html
│  │  └─ subsection1-1-2.html
│  └─ section1-2.html
├─ chapter2.html
│  ├─ section2-1.html
│  └─ section2-2.html
└─ appendix.html
```

When you run:
```bash
python convert_html_to_pdf.py --merge-linked index.html complete_doc.pdf
```

The script will:
1. Start with `index.html`
2. Find and follow links to `chapter1.html`, `chapter2.html`, and `appendix.html`
3. From `chapter1.html`, follow links to `section1-1.html` and `section1-2.html`
4. From `section1-1.html`, follow links to `subsection1-1-1.html` and `subsection1-1-2.html`
5. Continue recursively until all linked HTML files are discovered
6. Merge all files in the discovered order into a single PDF

This is particularly useful for:
- API documentation with nested structure
- Technical manuals with multiple chapters and sections
- Multi-page reports with cross-references
- Any HTML documentation that uses a hierarchical link structure

## Important Notes

- The library uses Playwright in the background, so it requires a browser environment
- Asynchronous functions are used, so the script must be run in an async context
- HTML files with complex CSS or JavaScript will be rendered as they would appear in a browser
- The recursive link following prevents infinite loops by tracking visited files
- External links (http://, https://, mailto:, etc.) are skipped during traversal
- Fragment identifiers (#anchors) are handled correctly during link resolution