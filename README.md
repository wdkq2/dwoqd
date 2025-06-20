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

In Google Colab you must expose the Flask server using `google.colab.output`
before starting it. Some environments may not provide `serve_kernel_port`, so
check for it first:

```python
from google.colab import output
if hasattr(output, "serve_kernel_port"):
    url = output.serve_kernel_port(8000)
    print(f"Open the web interface at: {url}")

!python web_app.py
```

This will provide a link in the cell output that opens the web interface.
The Flask app itself does not call `serve_kernel_port`, so make sure to run
these commands first when using Colab.


### Google Colab에서 자세히 실행하기

1. 새 Colab 노트북에서 저장소를 가져오고 필요한 패키지를 설치합니다.

   ```bash
   !git clone <저장소 URL>
   %cd dwoqd
   !pip install -r requirements.txt
   !apt-get -y install poppler-utils
   ```

2. 다음 코드를 실행해 Flask 서버를 노트북 외부에서 접근할 수 있도록 노출합니다. 일부 환경에서는 `serve_kernel_port`가 없을 수 있으므로 조건을 확인합니다.

   ```python
   from google.colab import output
   if hasattr(output, "serve_kernel_port"):
       url = output.serve_kernel_port(8000)
       print(f"Open the web interface at: {url}")
   !python web_app.py
   ```

   웹 앱은 자동으로 `serve_kernel_port`를 호출하지 않으므로, 링크를 받으려면
   위 코드를 먼저 실행해야 합니다.

3. 셀 출력에 나타나는 링크를 클릭하면 웹 인터페이스가 열립니다. 여기서 PDF 파일,
   Google 서비스 계정 JSON, OpenAI API 키, 프롬프트를 한 번에 입력하면 됩니다.
   분석이 끝나면 **History** 페이지에서 결과를 확인하고 원하는 시점에
   Google Docs로 저장할 수 있습니다.

