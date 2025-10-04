#!/bin/bash

# Script to download Intel Simics Model Builder User Guide documentation
# This script will mirror the documentation site locally for offline access

echo "Starting download of Intel Simics Model Builder User Guide..."
echo "URL: https://intel.github.io/simics/docs/model-builder-user-guide"
echo

# Create a directory for the download
mkdir -p simics_docs
cd simics_docs

# Use wget to mirror the documentation site
# --mirror: Turn on recursive downloading with infinite recursion depth
# --convert-links: Convert links for local viewing
# --adjust-extension: Adjust suffixes for better viewing
# --page-requisites: Download CSS, JS, and other required files
# --no-parent: Don't go up in the directory structure
# --random-wait: Add random wait between requests to be respectful

wget \
  --mirror \
  --convert-links \
  --adjust-extension \
  --page-requisites \
  --no-parent \
  --random-wait \
  --wait=1 \
  https://intel.github.io/simics/docs/model-builder-user-guide

echo
echo "Download completed. The documentation is available in the simics_docs folder."
echo "To view it locally, open the index.html file in your browser:"
echo "  cd simics_docs/intel.github.io/simics/docs/model-builder-user-guide/"
echo "  firefox index.html # or your preferred browser"
