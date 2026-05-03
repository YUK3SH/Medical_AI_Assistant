# MedicAI — Medical Document Assistant

MedicAI is a simple web app we built to help people understand their medical documents without getting confused by all the medical terms. You can upload a PDF like a lab report or prescription, and it gives you a clean summary of what it says in simple language. There's also a chatbot where you can ask general medical questions and get straightforward answers.

One thing we made sure of is that the chatbot never tries to diagnose anything. It always tells you to consult a doctor for anything serious. We didn't want to build something that gives people false confidence about their health.

#### Try -> https://azureaws.vercel.app/
---

## What you can do with it

- Upload a medical PDF and get a simple point by point summary of what it contains
- Ask the chatbot general health questions and get easy to understand responses
- The chatbot always reminds you to consult a doctor for anything serious

---

## How we built it

The backend is written in Python using Flask. We used three Azure services to make it work.

When you upload a file, it first goes to Azure Blob Storage which basically just stores it in the cloud. Then Azure Document Intelligence reads through the PDF and pulls out all the text from it. After that, Azure OpenAI takes that extracted text and summarizes it in simple bullet points. The same OpenAI service also powers the chatbot.

The frontend is plain HTML and CSS — nothing fancy, just clean and functional pages for the home screen, the summarizer, and the chatbot.

We stored all the API keys in a `.env` file and made sure it's excluded from GitHub so nothing sensitive gets exposed.

---

## Running it locally

You'll need Python 3.10 or above and an Azure account with Document Intelligence, Blob Storage, and OpenAI resources set up.

Clone the repo and install the dependencies first.

```bash
git clone https://github.com/YUK3SH/Medical_AI_Assistant
cd azureaws
pip install -r requirements.txt
```

Then create a `.env` file in the root folder and add your Azure credentials like this.

```
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER=your_container_name
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

Then just run the app.

```bash
python app.py
```
## Getting your Azure keys

For Document Intelligence, go to the Azure portal, create a Document Intelligence resource, and once it's deployed you'll find the key and endpoint under Keys and Endpoint in the left sidebar.

For Azure OpenAI, go to ai.azure.com, open your OpenAI resource, and the key and endpoint are in the same place. You'll also need the deployment name from the Model Deployments section.

For Blob Storage, create a Storage Account in the portal, make a container inside it, and copy the connection string from the Access Keys section.
