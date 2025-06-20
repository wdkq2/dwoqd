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

## Web Interface

The repository includes a Flask application that lets you upload a PDF and analyze it in the browser. Processed PDFs are stored in a history page so you can review the results and decide when to save them.

Run the server:

```bash
python web_app.py
```

Open `http://localhost:8000` in your browser and fill out the form with the PDF file, Google service account JSON, OpenAI API key, and optional prompt. After processing, visit the **History** page to see the results. From there you can choose a document title and save the images and descriptions to a new Google Doc whenever you need.
