# 🤖 Asquify

**Asquify** is an AI-powered FastAPI application that transforms any PDF into a set of insightful, exam-style questions and answers. Powered by large language models (LLMs) and vector-based search, Asquify is perfect for students, educators, and developers preparing for coding tests, technical interviews, or self-paced learning.

---

## 🚀 Features

- 📄 Upload a PDF file (e.g., notes, docs, manuals).
- 🔍 Automatically generate relevant questions from the content.
- 💬 Get high-quality answers using intelligent document retrieval.
- 🧠 Uses LangChain, FAISS, and HuggingFace embeddings.
- 📁 Export Q&A as a CSV file.
- ⚡ FastAPI-based backend for high performance.

---

## 🧰 Tech Stack

- **Backend:** FastAPI  
- **LLMs:** LLaMA3 via `ChatOllama`  
- **Vector Store:** FAISS  
- **Embeddings:** HuggingFace Transformers (`sentence-transformers`)  
- **Document Parsing:** PyPDF2, pypdf, LangChain loaders  
- **Templating:** Jinja2  

---

## 🛠 Installation

### 1. Clone the Repository



### 2. Install Dependencies  
*(Using a virtual environment is recommended)*

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
uvicorn app:app --reload
```

### 4. Access the App

Open your browser and visit:

```text
http://127.0.0.1:8000
```

---

## 📂 Project Structure

```text
asquify/
├── app.py               # Main FastAPI app
├── templates/           # Jinja2 templates
├── static/
│   ├── docs/            # Uploaded PDF files
│   └── output/          # Exported Q&A CSVs
├── requirements.txt     # Python dependencies
```

---

## 💡 How It Works

1. Upload a PDF document via the UI.  
2. Asquify processes and chunks the text.  
3. It uses LLaMA3 (via Ollama) to generate meaningful questions.  
4. Then it uses a vector search (FAISS + HuggingFace) to answer them.  
5. Download the results as a neat CSV file!

---

## 📘 Use Cases

- 🚀 Interview prep from technical documents  
- 🎓 Create quizzes from lecture notes  
- 📚 Self-study from textbooks and PDFs  

---

## ⚙️ Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) running locally with the LLaMA3 model — run using:

```bash
ollama run llama3
```

- A modern browser for the frontend

---


