import os
import requests
from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv


# Load environment variables from .env if present
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/summarizer")
def summarizer():
    return render_template("summarizer.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


def upload_file_to_blob(file_path, container_name="uploads"):
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    container_client = blob_service_client.get_container_client(container_name)

    try:
        container_client.get_container_properties()
    except Exception:
        container_client.create_container()

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=os.path.basename(file_path)
    )

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    return blob_client.url


def extract_text(file_url):
    if not DOCUMENT_INTELLIGENCE_ENDPOINT or not DOCUMENT_INTELLIGENCE_KEY:
        raise RuntimeError("Document Intelligence endpoint/key not set")

    client = DocumentIntelligenceClient(
        DOCUMENT_INTELLIGENCE_ENDPOINT, AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
    )
    poller = client.begin_analyze_document("prebuilt-read", {"urlSource": file_url})
    result = poller.result()

    text_content = "\n".join(
        [line.content for page in result.pages for line in page.lines]
    )
    return text_content


def summarize_text(text):
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY or not AZURE_OPENAI_DEPLOYMENT:
        raise RuntimeError("Azure OpenAI config not set (endpoint/key/deployment)")

    url = f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2025-01-01-preview"
    headers = {"Authorization": f"Bearer {AZURE_OPENAI_KEY}", "Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": "Summarize the following document in key points."},
            {"role": "user", "content": text},
        ],
        "max_tokens": 500,
    }

    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json().get("choices", [])[0].get("message", {}).get("content", "")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY or not AZURE_OPENAI_DEPLOYMENT:
        return jsonify({"error": "Azure OpenAI not configured on server"}), 500

    system_prompt = (
        "You are MediAssist, an AI medical assistant specialized in providing general health information. "
        "You MUST state that you are not a substitute for professional medical advice and never provide definitive diagnoses."
    )

    url = f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2025-01-01-preview"
    headers = {"Authorization": f"Bearer {AZURE_OPENAI_KEY}", "Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json().get("choices", [])[0].get("message", {}).get("content", "")
        disclaimer = "\n\n*Disclaimer: This information is for educational purposes only and not a substitute for professional medical advice.*"
        full_reply = reply + disclaimer
        return jsonify({"reply": full_reply})
    except Exception as e:
        return jsonify({"error": f"Error processing medical request: {str(e)}"}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = file.filename
    file.save(file_path)

    try:
        file_url = upload_file_to_blob(file_path)
        extracted_text = extract_text(file_url)
        summary = summarize_text(extracted_text)
        return jsonify({"filename": file.filename, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
