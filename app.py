from fastapi import FastAPI, Form, Request, Response, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from langchain_community.chat_models import ChatOllama
from langchain.chains import QAGenerationChain
from langchain.text_splitter import TokenTextSplitter
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
import os 
import json
import time
import uvicorn
import aiofiles
from PyPDF2 import PdfReader
import csv

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def count_pdf_pages(pdf_path):
    try:
        pdf = PdfReader(pdf_path)
        return len(pdf.pages)
    except Exception as e:
        print("Error:", e)
        return None

def file_processing(file_path):
    loader = PyPDFLoader(file_path)
    data = loader.load()
    question_gen = ''.join([page.page_content for page in data])

    splitter_ques_gen = TokenTextSplitter(
        model_name='gpt-3.5-turbo',  # Still needed by Langchain for chunking logic
        chunk_size=10000,
        chunk_overlap=200
    )
    chunks_ques_gen = splitter_ques_gen.split_text(question_gen)
    document_ques_gen = [Document(page_content=t) for t in chunks_ques_gen]

    splitter_ans_gen = TokenTextSplitter(
        model_name='gpt-3.5-turbo',
        chunk_size=1000,
        chunk_overlap=100
    )
    document_answer_gen = splitter_ans_gen.split_documents(document_ques_gen)
    return document_ques_gen, document_answer_gen

def llm_pipeline(file_path):
    document_ques_gen, document_answer_gen = file_processing(file_path)

    llm_ques_gen_pipeline = ChatOllama(
        model="llama3",  # or "mistral", "codellama"
        temperature=0.3
    )

    prompt_template = """
    You are an expert at creating questions based on coding materials and documentation.
    Your goal is to prepare a coder or programmer for their exam and coding tests.
    You do this by asking questions about the text below:

    ------------
    {text}
    ------------

    Create questions that will prepare the coders or programmers for their tests.
    Make sure not to lose any important information.

    QUESTIONS:
    """

    PROMPT_QUESTIONS = PromptTemplate(template=prompt_template, input_variables=["text"])

    refine_template = """
    You are an expert at creating practice questions based on coding material and documentation.
    Your goal is to help a coder or programmer prepare for a coding test.
    We have received some practice questions to a certain extent: {existing_answer}.
    We have the option to refine the existing questions or add new ones (only if necessary) with some more context below.
    ------------
    {text}
    ------------

    Given the new context, refine the original questions in English.
    If the context is not helpful, please provide the original questions.
    QUESTIONS:
    """

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template
    )

    ques_gen_chain = load_summarize_chain(
        llm=llm_ques_gen_pipeline,
        chain_type="refine",
        verbose=True,
        question_prompt=PROMPT_QUESTIONS,
        refine_prompt=REFINE_PROMPT_QUESTIONS
    )

    ques = ques_gen_chain.run(document_ques_gen)

    # Use HuggingFace for offline embeddings (or keep OpenAIEmbeddings if you want)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store = FAISS.from_documents(document_answer_gen, embeddings)

    llm_answer_gen = ChatOllama(
        model="llama3",
        temperature=0.1
    )

    ques_list = ques.split("\n")
    filtered_ques_list = [element for element in ques_list if element.endswith('?') or element.endswith('.')]

    answer_generation_chain = RetrievalQA.from_chain_type(
        llm=llm_answer_gen,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )

    return answer_generation_chain, filtered_ques_list


def get_csv(file_path):
    answer_generation_chain, ques_list = llm_pipeline(file_path)
    base_folder = 'static/output/'
    if not os.path.isdir(base_folder):
        os.mkdir(base_folder)
    output_file = base_folder + "QA.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Question", "Answer"])

        for question in ques_list:
            print("Question: ", question)
            answer = answer_generation_chain.run(question)
            print("Answer: ", answer)
            print("--------------------------------------------------\n\n")
            csv_writer.writerow([question, answer])

    return output_file


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def chat(request: Request, pdf_file: bytes = File(), filename: str = Form(...)):
    base_folder = 'static/docs/'
    if not os.path.isdir(base_folder):
        os.mkdir(base_folder)
    pdf_filename = os.path.join(base_folder, filename)

    async with aiofiles.open(pdf_filename, 'wb') as f:
        await f.write(pdf_file)

    response_data = jsonable_encoder(json.dumps({"msg": 'success', "pdf_filename": pdf_filename}))
    res = Response(response_data)
    return res


@app.post("/analyze")
async def chat(request: Request, pdf_filename: str = Form(...)):
    try:
        output_file = get_csv(pdf_filename)
        response_data = jsonable_encoder(json.dumps({"output_file": output_file}))
        return Response(response_data)
    except Exception as e:
        print("ERROR:", e)
        return Response(jsonable_encoder(json.dumps({"msg": f"error: {str(e)}"})), status_code=500)


if __name__ == "__main__":
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)
