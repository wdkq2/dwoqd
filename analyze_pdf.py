import os
import io
import base64
import argparse
from pdf2image import convert_from_path
from googleapiclient.discovery import build
from google.oauth2 import service_account
import openai


def pdf_to_images(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, img in enumerate(images):
        out_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        img.save(out_path, 'JPEG')
        image_paths.append(out_path)
    return image_paths


def call_openai(image_path, prompt):
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def get_docs_service(credentials_path):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/documents']
    )
    return build('docs', 'v1', credentials=creds)


def append_image_and_text(service, doc_id, image_path, text):
    with open(image_path, 'rb') as f:
        image_content = f.read()

    requests = [
        {
            'insertInlineImage': {
                'location': {
                    'endOfSegmentLocation': {}
                },
                'objectSize': {
                    'height': {'magnitude': 500, 'unit': 'PT'},
                    'width': {'magnitude': 400, 'unit': 'PT'}
                },
                'uri': 'data:image/jpeg;base64,' + base64.b64encode(image_content).decode('utf-8')
            }
        },
        {
            'insertText': {
                'endOfSegmentLocation': {},
                'text': '\n' + text + '\n\n'
            }
        }
    ]
    service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()


def main():
    parser = argparse.ArgumentParser(description='Analyze PDF pages with OpenAI and save results to Google Docs.')
    parser.add_argument('--pdf', required=True, help='Input PDF file')
    parser.add_argument('--output-dir', default='output_images', help='Directory to save JPG pages')
    parser.add_argument('--prompt', default='Describe the page', help='Prompt to analyze each page')
    parser.add_argument('--google-credentials', required=True, help='Path to Google service account JSON credentials')
    parser.add_argument('--doc-id', required=True, help='Google Docs document ID to append results to')
    args = parser.parse_args()

    openai.api_key = os.environ.get('OPENAI_API_KEY')
    if not openai.api_key:
        raise RuntimeError('OPENAI_API_KEY environment variable not set')

    service = get_docs_service(args.google_credentials)

    image_paths = pdf_to_images(args.pdf, args.output_dir)
    for img_path in image_paths:
        description = call_openai(img_path, args.prompt)
        append_image_and_text(service, args.doc_id, img_path, description)
        print(f'Processed {img_path}')


if __name__ == '__main__':
    main()
