# PDF Analyzer Automation

This repository contains a script to convert a PDF into JPG files, analyze each page using the OpenAI API, and append the images and analysis to a Google Docs document.

## Requirements

- Python 3.11+
- `pdftoppm` from Poppler (install with `apt-get install poppler-utils` on Debian/Ubuntu)
- Python packages listed in `requirements.txt`
- Google service account credentials with access to Google Docs
- `OPENAI_API_KEY` environment variable

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python analyze_pdf.py --pdf path/to/file.pdf \
                      --google-credentials path/to/credentials.json \
                      --doc-id YOUR_GOOGLE_DOC_ID
```

The script will save JPG files in the `output_images` directory, analyze each page, and append the images and their descriptions to the specified Google Doc.
