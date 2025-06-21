from flask import Flask, request, render_template_string, redirect, url_for
import os
import tempfile
import base64

from analyze_pdf import (
    pdf_to_images,
    call_openai,
    get_docs_service,
    append_image_and_text,
    create_document,
)


app = Flask(__name__)

history = []


INDEX_HTML = """
<!doctype html>
<title>PDF Analyzer</title>
<h1>Upload PDF</h1>
<form method="post" enctype="multipart/form-data">
  <label>PDF File: <input type="file" name="pdf" required></label><br>
  <label>Google Credentials JSON: <input type="file" name="credentials" required></label><br>
  <label>OpenAI API Key: <input type="text" name="openai_api_key" required></label><br>
  <label>Prompt:<br>
    <textarea name="prompt" rows="4" cols="50">Describe the page</textarea>
  </label><br>
  <input type="submit" value="Analyze">
</form>
<p>{{ message }}</p>
<p><a href="{{ url_for('history_page') }}">History</a></p>
"""


HISTORY_HTML = """
<!doctype html>
<title>History</title>
<h1>Analysis History</h1>
<ul>
{% for item in history %}
  <li><a href="{{ url_for('view_item', item_id=item.id) }}">{{ item.title }}</a></li>
{% endfor %}
</ul>
<p><a href="{{ url_for('index') }}">Upload another PDF</a></p>
"""


DETAIL_HTML = """
<!doctype html>
<title>{{ item.title }}</title>
<h1>{{ item.title }}</h1>
{% for entry in item.results %}
  <div>
    <img src="data:image/jpeg;base64,{{ entry.img_b64 }}" width="400"><br>
    <pre>{{ entry.description }}</pre>
  </div>
  <hr>
{% endfor %}
<form method="post" action="{{ url_for('save', item_id=item.id) }}">
  <label>Document title: <input type="text" name="title" value="{{ item.title }}"></label>
  <input type="submit" value="Save to Google Docs">
</form>
<p>{{ message }}</p>
<p><a href="{{ url_for('history_page') }}">Back to history</a></p>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        cred_file = request.files.get('credentials')
        openai_key = request.form.get('openai_api_key')
        prompt = request.form.get('prompt', 'Describe the page')

        if pdf_file and cred_file and openai_key:
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, 'input.pdf')
                pdf_file.save(pdf_path)
                creds_json = cred_file.read().decode('utf-8')

                os.environ['OPENAI_API_KEY'] = openai_key

                results = []
                for img_path in pdf_to_images(pdf_path, tmpdir):
                    description = call_openai(img_path, prompt)
                    with open(img_path, 'rb') as img_f:
                        img_b64 = base64.b64encode(img_f.read()).decode('utf-8')
                    results.append({'img_b64': img_b64, 'description': description})

            item_id = len(history)
            history.append({
                'id': item_id,
                'title': os.path.basename(pdf_file.filename),
                'prompt': prompt,
                'results': results,
                'credentials_json': creds_json,
            })
            return redirect(url_for('view_item', item_id=item_id))
        else:
            message = 'Missing required fields.'
    return render_template_string(INDEX_HTML, message=message)


@app.route('/history')
def history_page():
    return render_template_string(HISTORY_HTML, history=history)


@app.route('/history/<int:item_id>')
def view_item(item_id):
    item = next((i for i in history if i['id'] == item_id), None)
    if not item:
        return 'Not found', 404
    return render_template_string(DETAIL_HTML, item=item, message='')


@app.route('/save/<int:item_id>', methods=['POST'])
def save(item_id):
    item = next((i for i in history if i['id'] == item_id), None)
    if not item:
        return 'Not found', 404

    title = request.form.get('title', item['title'])

    with tempfile.NamedTemporaryFile('w+', delete=False) as cred_tmp:
        cred_tmp.write(item['credentials_json'])
        cred_tmp.flush()
        service = get_docs_service(cred_tmp.name)

    doc_id = create_document(service, title)

    for entry in item['results']:
        with tempfile.NamedTemporaryFile(suffix='.jpg') as img_tmp:
            img_tmp.write(base64.b64decode(entry['img_b64']))
            img_tmp.flush()
            append_image_and_text(service, doc_id, img_tmp.name, entry['description'])

    message = f'Saved to Google Docs: {doc_id}'
    return render_template_string(DETAIL_HTML, item=item, message=message)


if __name__ == '__main__':
    # The Flask server runs on port 8000. When executed in Google Colab,
    # we try to expose the URL automatically. Older Colab versions may not
    # provide `serve_kernel_port`, so we fall back to `kernel.proxyPort`.
    url = None

    try:
        from google.colab import output
        if hasattr(output, "serve_kernel_port"):
            url = output.serve_kernel_port(8000)
        else:
            url = output.eval_js("google.colab.kernel.proxyPort(8000)")
    except Exception:
        pass

    if url:
        print(f"Open the web interface at: {url}")

    app.run(host="0.0.0.0", port=8000)
