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

### Running in Google Colab

`web_app.py` automatically exposes the Flask server in Google Colab. It first
tries `google.colab.output.serve_kernel_port`, falling back to
`google.colab.kernel.proxyPort` if needed. When you run the script, it prints a
link such as `Open the web interface at: <url>`. Click that link to access the
web app. If no link appears, your environment may not support these helpers and
you will need to manually expose port 8000.

```bash
python web_app.py
```

The script prints something like `Open the web interface at: <url>` when run in
Colab. Open that link to access the web app.

### Google Colab에서 자세히 실행하기

1. 새 Colab 노트북에서 저장소를 가져오고 필요한 패키지를 설치합니다.

   ```bash
   !git clone <저장소 URL>
   %cd dwoqd
   !pip install -r requirements.txt
   !apt-get -y install poppler-utils
   ```

2. `web_app.py`를 실행합니다. 스크립트가 자동으로 포트를 노출하고 URL을
   출력합니다. 지원되지 않는 경우에는 아래 예시처럼 수동으로 포트를
   노출한 뒤 표시되는 링크를 사용합니다.

   ```bash
   !python web_app.py
   ```

   셀은 계속 실행 중이므로, 새로운 셀을 열어 아래 코드를 실행하여 링크를
   얻을 수 있습니다.

   ```python
   from google.colab import output
   output.eval_js("google.colab.kernel.proxyPort(8000)")
   ```

   표시되는 링크를 클릭하면 웹 인터페이스로 이동합니다.

3. 셀 출력에 나타나는 링크를 클릭하면 웹 인터페이스가 열립니다. 여기서 PDF 파일,
   Google 서비스 계정 JSON, OpenAI API 키, 프롬프트를 한 번에 입력하면 됩니다.
   분석이 끝나면 **History** 페이지에서 결과를 확인하고 원하는 시점에
   Google Docs로 저장할 수 있습니다.
