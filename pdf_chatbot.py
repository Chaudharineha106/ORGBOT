from transformers import pipeline
from PyPDF2 import PdfReader
import docx
from dotenv import load_dotenv
import os

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")

print("Loading model... (this may take a minute on first run)")
qa_pipeline = pipeline("text2text-generation", model=MODEL_NAME)

# Global variable to hold memory content
memory_context = ""

def get_memory_context():
    global memory_context
    return memory_context

def set_memory_context(content):
    global memory_context
    memory_context = content

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(file):
    text = file.read().decode("utf-8")
    return text

def generate_answer(question):
    context = get_memory_context()
    prompt = f"Answer the question based on the following context:\nContext: {context}\nQuestion: {question}"
    response = qa_pipeline(prompt, max_length=200, do_sample=True, temperature=0.7, top_p=0.9)
    return response[0]["generated_text"]
