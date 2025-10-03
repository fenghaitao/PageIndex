#!/usr/bin/env python3
"""
Script to convert local HTML files to PDF using pwhtmltopdf library.
"""

import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
import tempfile
import re

from bs4 import BeautifulSoup
from pwhtmltopdf import HtmlToPdf


async def convert_html_to_pdf(html_file_path, pdf_output_path=None, pdf_options=None):
    """
    Convert a local HTML file to PDF using pwhtmltopdf.
    
    Args:
        html_file_path (str or Path): Path to the input HTML file
        pdf_output_path (str or Path, optional): Path for the output PDF file
        pdf_options (dict, optional): Options for PDF generation
    
    Returns:
        bytes: PDF content if no output path is provided
    """
    
    # If no PDF output path is provided, create one based on the HTML file name
    if pdf_output_path is None:
        html_path = Path(html_file_path)
        pdf_output_path = html_path.with_suffix('.pdf')
    
    # Set default PDF options if not provided
    if pdf_options is None:
        pdf_options = {
            'format': 'A4',
            'print_background': True,
            'margin': {
                'top': '20px',
                'bottom': '20px',
                'left': '20px',
                'right': '20px'
            }
        }
    
    # Create HtmlToPdf instance with PDF options
    converter = HtmlToPdf(pdf_kwargs=pdf_options)
    
    try:
        # Convert the HTML file to PDF
        pdf_content = await converter.from_file(
            file=html_file_path,
            output_path=pdf_output_path
        )
        
        print(f"Successfully converted '{html_file_path}' to '{pdf_output_path}'")
        return pdf_content
        
    except Exception as e:
        print(f"Error converting HTML to PDF: {str(e)}")
        raise
    finally:
        # Close the converter
        await converter.close()


async def merge_linked_html_to_pdf(index_file_path, pdf_output_path=None, pdf_options=None):
    """
    Follow all links in an index HTML file and merge all content into a single PDF.
    
    Args:
        index_file_path (str or Path): Path to the index HTML file
        pdf_output_path (str or Path, optional): Path for the output PDF file
        pdf_options (dict, optional): Options for PDF generation
    
    Returns:
        bytes: PDF content if no output path is provided
    """
    index_path = Path(index_file_path)
    
    # If no PDF output path is provided, create one based on the index file name
    if pdf_output_path is None:
        pdf_output_path = index_path.with_suffix('.pdf')
    
    # Set default PDF options if not provided
    if pdf_options is None:
        pdf_options = {
            'format': 'A4',
            'print_background': True,
            'margin': {
                'top': '20px',
                'bottom': '20px',
                'left': '20px',
                'right': '20px'
            }
        }
    
    # Parse the index file to extract links in order
    with open(index_file_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    soup = BeautifulSoup(index_content, 'html.parser')
    
    # Collect all unique links from the index file in the order they appear
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Skip external links and anchors
        if href.startswith(('http', 'https', 'mailto:', '#', 'javascript:')):
            continue
        # Make relative paths absolute
        abs_path = (index_path.parent / href).resolve()
        if abs_path.exists() and str(abs_path) not in links:
            links.append(str(abs_path))
    
    # Add the index file itself as the first item, then all linked files in order
    all_files = [str(index_path.resolve())] + [link for link in links if Path(link).exists()]
    
    print(f"Found {len(all_files)} HTML files to merge: {all_files}")
    
    # Create a temporary HTML file that combines all content
    combined_html = '<!DOCTYPE html><html><head><meta charset="utf-8">'
    combined_html += '<title>Combined Document</title>'
    
    # Extract and combine all CSS styles from the HTML files
    all_css = []
    for html_file in all_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            file_soup = BeautifulSoup(content, 'html.parser')
            
            # Extract any embedded styles
            for style_tag in file_soup.find_all('style'):
                all_css.append(style_tag.decode_contents())
            
            # Extract CSS files
            for link_tag in file_soup.find_all('link', rel='stylesheet'):
                css_href = link_tag.get('href')
                if css_href:
                    css_path = (Path(html_file).parent / css_href).resolve()
                    if css_path.exists():
                        with open(css_path, 'r', encoding='utf-8') as css_file:
                            all_css.append(css_file.read())
    
    # Add combined CSS
    if all_css:
        combined_html += '<style>' + '\n'.join(all_css) + '</style>'
    
    combined_html += '</head><body>'
    
    # Create a map to convert file paths to internal anchor IDs
    file_to_anchor = {}
    for i, html_file in enumerate(all_files):
        file_to_anchor[html_file] = f"section-{i}"
    
    # Add content from each file with appropriate separation and named anchors
    for i, html_file in enumerate(all_files):
        # Add a named anchor for internal navigation
        anchor_name = f"section-{i}"
        combined_html += f'<div id="{anchor_name}" style="margin-top: 40px;">'
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            file_soup = BeautifulSoup(content, 'html.parser')
            
            # Process all links in the content to convert them to internal anchors
            for link_tag in file_soup.find_all('a', href=True):
                href = link_tag.get('href')
                # Only process internal links (not external, mailto, etc.)
                if not href.startswith(('http', 'https', 'mailto:', '#', 'javascript:')):
                    try:
                        # Convert relative path to absolute
                        link_abs_path = (Path(html_file).parent / href).resolve()
                        link_abs_str = str(link_abs_path)
                        
                        # Check if this link points to one of our merged files
                        for merged_file in all_files:
                            if link_abs_str == merged_file:
                                # Change the href to point to the internal anchor
                                link_tag['href'] = f'#{file_to_anchor[merged_file]}'
                                break
                    except:
                        # If there's an issue with path resolution, keep the original link
                        pass
            
            # Extract and add body content
            body = file_soup.find('body')
            if body:
                body_content = str(body.decode_contents())
                # Add a separator between documents
                if i > 0:
                    combined_html += '<div style="page-break-before: always; height: 20px;"></div>'
                combined_html += f'<!-- Content from {html_file} -->'
                combined_html += body_content
            else:
                # If no body tag, just add the content
                if i > 0:
                    combined_html += '<div style="page-break-before: always; height: 20px;"></div>'
                combined_html += f'<!-- Content from {html_file} -->'
                combined_html += str(file_soup)
        
        combined_html += '</div>'  # Close the section div
    
    combined_html += '</body></html>'
    
    # Write the combined HTML to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(combined_html)
        temp_html_path = temp_file.name
    
    try:
        # Convert the combined HTML to PDF
        converter = HtmlToPdf(pdf_kwargs=pdf_options)
        pdf_content = await converter.from_file(
            file=temp_html_path,
            output_path=pdf_output_path
        )
        
        print(f"Successfully merged {len(all_files)} HTML files into '{pdf_output_path}' with internal navigation")
        return pdf_content
        
    except Exception as e:
        print(f"Error merging HTML files to PDF: {str(e)}")
        raise
    finally:
        # Close the converter
        await converter.close()
        # Clean up the temporary file
        Path(temp_html_path).unlink(missing_ok=True)


async def convert_multiple_html_files(html_directory, output_directory=None, pdf_options=None):
    """
    Convert all HTML files in a directory to PDF.
    
    Args:
        html_directory (str or Path): Directory containing HTML files
        output_directory (str or Path, optional): Directory for output PDFs
        pdf_options (dict, optional): Options for PDF generation
    """
    html_dir = Path(html_directory)
    
    if output_directory is None:
        output_directory = html_dir
    else:
        Path(output_directory).mkdir(parents=True, exist_ok=True)
    
    # Find all HTML files in the directory
    html_files = list(html_dir.glob('*.html')) + list(html_dir.glob('*.htm'))
    
    if not html_files:
        print(f"No HTML files found in '{html_directory}'")
        return
    
    print(f"Found {len(html_files)} HTML files to convert")
    
    for html_file in html_files:
        pdf_output_path = Path(output_directory) / f"{html_file.stem}.pdf"
        await convert_html_to_pdf(html_file, pdf_output_path, pdf_options)


def create_sample_html(file_path):
    """Create a sample HTML file for testing."""
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample HTML for PDF Conversion</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            margin: 20px 0;
            padding: 20px;
            background-color: white;
            border-radius: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Sample HTML Document</h1>
        <p>This is a sample HTML document for PDF conversion</p>
    </div>
    
    <div class="content">
        <h2>About This Document</h2>
        <p>This document demonstrates the capabilities of converting HTML to PDF using pwhtmltopdf library. It includes:</p>
        <ul>
            <li>Styled text with CSS</li>
            <li>Tables with borders</li>
            <li>Formatted headings and paragraphs</li>
            <li>Background colors</li>
        </ul>
        
        <h2>Sample Table</h2>
        <table>
            <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Category</th>
            </tr>
            <tr>
                <td>Widget A</td>
                <td>$19.99</td>
                <td>Electronics</td>
            </tr>
            <tr>
                <td>Widget B</td>
                <td>$29.99</td>
                <td>Home</td>
            </tr>
            <tr>
                <td>Widget C</td>
                <td>$39.99</td>
                <td>Office</td>
            </tr>
        </table>
        
        <h2>Additional Content</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
    </div>
    
    <div class="footer">
        <p>Generated on: October 3, 2025</p>
    </div>
</body>
</html>"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created sample HTML file: {file_path}")


async def main():
    """Main function to demonstrate the HTML to PDF conversion."""
    
    if len(sys.argv) < 2:
        print("Usage: python convert_html_to_pdf.py <html_file_path> [pdf_output_path]")
        print("   or: python convert_html_to_pdf.py <html_directory> [output_directory]")
        print("   or: python convert_html_to_pdf.py --create-sample <sample_file_path>")
        print("   or: python convert_html_to_pdf.py --merge-linked <index_html_file> [pdf_output_path]")
        return
    
    command = sys.argv[1]
    
    if command == "--create-sample":
        if len(sys.argv) < 3:
            print("Please provide a path for the sample HTML file")
            return
        
        sample_path = sys.argv[2]
        create_sample_html(sample_path)
        return
    
    if command == "--merge-linked":
        if len(sys.argv) < 3:
            print("Please provide an index HTML file to process")
            return
        
        index_path = Path(sys.argv[2])
        if not index_path.exists():
            print(f"Error: Index file '{index_path}' does not exist")
            return
        
        output_path = None
        if len(sys.argv) > 3:
            output_path = sys.argv[3]
        
        # Define PDF options
        pdf_options = {
            'format': 'A4',
            'print_background': True,
            'margin': {
                'top': '20px',
                'bottom': '20px',
                'left': '20px',
                'right': '20px'
            }
        }
        
        await merge_linked_html_to_pdf(index_path, output_path, pdf_options)
        return
    
    # Define PDF options
    pdf_options = {
        'format': 'A4',
        'print_background': True,
        'margin': {
            'top': '20px',
            'bottom': '20px',
            'left': '20px',
            'right': '20px'
        }
    }
    
    input_path = Path(sys.argv[1])
    
    if input_path.is_file() and input_path.suffix.lower() in ['.html', '.htm']:
        # Convert single HTML file
        output_path = None
        if len(sys.argv) > 2:
            output_path = sys.argv[2]
        
        await convert_html_to_pdf(input_path, output_path, pdf_options)
        
    elif input_path.is_dir():
        # Convert all HTML files in directory
        output_dir = None
        if len(sys.argv) > 2:
            output_dir = sys.argv[2]
        
        await convert_multiple_html_files(input_path, output_dir, pdf_options)
        
    else:
        print(f"Error: '{input_path}' is not a valid HTML file or directory")
        return


if __name__ == "__main__":
    asyncio.run(main())