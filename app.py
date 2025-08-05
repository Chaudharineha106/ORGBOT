from flask import Flask, request, jsonify, render_template, session, redirect , url_for
from Bot_Final import UltraChatBot
import json
import firebase_admin
from firebase_admin import credentials, db
import os
import pdfplumber
import re
import nltk
from transformers import T5Tokenizer, T5ForConditionalGeneration
#from pdf_chatbot import extract_text_from_pdf, generate_answer
from pdf_chatbot import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    generate_answer,
    get_memory_context,
    set_memory_context
)

# Ensure NLTK tokenizer is available
from nltk.tokenize import sent_tokenize

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Firebase Admin SDK
cred = credentials.Certificate("fbconfig.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://projectcg4-6c3b1-default-rtdb.firebaseio.com/'
})

PROJECT_UPLOAD_FOLDER = "uploads"  # Inside the project directory
#EXTERNAL_UPLOAD_FOLDER = "D:/Saved_PDFs"  # Specific location in D drive

# Ensure both folders exist
os.makedirs(PROJECT_UPLOAD_FOLDER, exist_ok=True)
#os.makedirs(EXTERNAL_UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def select():
    return render_template('select.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    for user_type in ['users', 'employees']:
        users_ref = db.reference(user_type)
        users_data = users_ref.get()
        if users_data:
            for user_id, user_info in users_data.items():
                if user_info.get("email") == email and user_info.get("password") == password:
                    session['user'] = user_id
                    session['user_type'] = user_type
                    return jsonify({"success": True, "redirect": "/bot"}), 200
    return jsonify({"success": False, "message": "Invalid credentials."}), 401

@app.route('/register', methods=['POST','GET'])
def register():
    data = request.json
    name, email, contact, password, confirm_password, user_type = data.values()
    
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match!"}), 400

    node = "users" if user_type == "user" else "employees"
    users_ref = db.reference(node)

    # ✅ Replace spaces with underscores to create a Firebase-safe key
    safe_name = name.replace(" ", "_")

    existing_users = users_ref.get() or {}
    if safe_name in existing_users:
        return jsonify({"success": False, "message": "Username already taken!"}), 409

    users_ref.child(safe_name).set({
        'email': email, 
        'contact': contact, 
        'password': password, 
        'user_type': user_type 
    })

    # ✅ Store the safe_name in session for future use
    session["user_name"] = safe_name  
    session["user_type"] = node  

    return jsonify({"success": True, "redirect": "/"}), 201


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login_page')

@app.route('/bot')
def index():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/mybot', methods=['POST'])
def mybot():
    user_type = session.get('user_type', 'user')
    user_message = request.json.get('data', '')
    bot = UltraChatBot(user_type)
    bot_response = bot.process_incoming_message(user_message)
    return jsonify(bot_response)

@app.route("/pdf.html")
def upload_pdf_page():
    return render_template("pdf.html")

import uuid
import datetime

# Updated upload route
@app.route("/upload_pdf", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = str(uuid.uuid4()) + "_" + file.filename
    file_extension = file.filename.split('.')[-1].lower()

    file_path = os.path.join(PROJECT_UPLOAD_FOLDER, filename)
    try:
        file.save(file_path)

        user_type = session.get("user_type")  # e.g., "employee"
        user_id = session.get("user")         # e.g., "surbhi"

        if not user_type or not user_id:
            return jsonify({"error": "Session user info missing"}), 400

        # ✅ Correct Firebase path
        user_ref = db.reference(f'{user_type}/{user_id}/uploaded_files')
        user_ref.push({
            'file_name': filename,
            'uploaded_at': str(datetime.datetime.now())
        })

        # ✅ File processing
        if file_extension == "txt":
            content = extract_text_from_txt(file)
        elif file_extension == "pdf":
            content = extract_text_from_pdf(file)
        elif file_extension == "docx":
            content = extract_text_from_docx(file)
        else:
            return jsonify({"error": "Unsupported file type. Please upload a .txt, .pdf, or .docx file."}), 400

        set_memory_context(content)

        return jsonify({
            "success": True,
            "message": "File uploaded and content stored!",
            "file_content": content
        })


        #return jsonify({"success": True, "message": "File uploaded and content stored!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ask", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    if not get_memory_context().strip():
        return jsonify({"error": "No memory found. Please upload a file first."}), 400

    answer = generate_answer(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=False)
