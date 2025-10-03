# HTML to PDF Converter using pwhtmltopdf

This script demonstrates how to convert local HTML files to PDF using the `pwhtmltopdf` library, which leverages Playwright for high-fidelity PDF generation.

## Features

- Convert individual HTML files to PDF
- Convert all HTML files in a directory to PDF
- Merge all linked content from an index HTML file into a single PDF
- Customizable PDF options (page size, margins, etc.)
- Support for CSS styling in the generated PDF
- Asynchronous processing for better performance

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

## Important Notes

- The library uses Playwright in the background, so it requires a browser environment
- Asynchronous functions are used, so the script must be run in an async context
- HTML files with complex CSS or JavaScript will be rendered as they would appear in a browser