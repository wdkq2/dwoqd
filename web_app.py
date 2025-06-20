from flask import Flask, request, render_template_string
import os
import tempfile
from analyze_pdf import pdf_to_images, call_openai, get_docs_service, append_image_and_text

HTML_PAGE = '''
<!doctype html>
<title>PDF Analyzer</title>
<h1>Upload PDF for Analysis</h1>
<form method="post" enctype="multipart/form-data">
  <label>PDF File: <input type="file" name="pdf" required></label><br>
  <label>Google Credentials JSON: <input type="file" name="credentials" required></label><br>
  <label>Google Doc ID: <input type="text" name="doc_id" required></label><br>
  <label>OpenAI API Key: <input type="text" name="openai_api_key" required></label><br>
  <label>Prompt:<br>
    <textarea name="prompt" rows="4" cols="50">Describe the page</textarea>
  </label><br>
  <input type="submit" value="Start">
</form>
<p>{{ message }}</p>
'''

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        cred_file = request.files.get('credentials')
        doc_id = request.form.get('doc_id')
        openai_key = request.form.get('openai_api_key')
        prompt = request.form.get('prompt', 'Describe the page')
        if pdf_file and cred_file and doc_id and openai_key:
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, 'input.pdf')
                cred_path = os.path.join(tmpdir, 'creds.json')
                pdf_file.save(pdf_path)
                cred_file.save(cred_path)
                os.environ['OPENAI_API_KEY'] = openai_key
                service = get_docs_service(cred_path)
                for img_path in pdf_to_images(pdf_path, tmpdir):
                    description = call_openai(img_path, prompt)
                    append_image_and_text(service, doc_id, img_path, description)
            message = 'Processing completed'
        else:
            message = 'Missing required fields.'
    return render_template_string(HTML_PAGE, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
