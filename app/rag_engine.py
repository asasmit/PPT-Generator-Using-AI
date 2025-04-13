import os
import json
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import re
from dotenv import load_dotenv
load_dotenv()

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama3-8b-8192"
VECTOR_DB_DIR = "vectorstore"

def extract_json_from_response(text):
    try:
        first_brace_index = text.index('{')
        json_str = text[first_brace_index:]
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        return {"error": f"Failed to extract/parse JSON: {e}", "raw": text}

def load_and_split_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

def build_vectorstore(docs, index_name):
    embedding = HuggingFaceEmbeddings()
    vectordb = FAISS.from_documents(docs, embedding)
    path = os.path.join(VECTOR_DB_DIR, index_name)
    vectordb.save_local(path)
    return vectordb

def query_vectorstore(subject, topic, subtopic, grade, vectordb):
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    context_docs = retriever.invoke(f"{topic} {subtopic}")
    context = "\n\n".join(doc.page_content for doc in context_docs)

    prompt = f"""
You are an educational assistant.

Based on the following:

- Grade: {grade}
- Subject: {subject}
- Topic: {topic}
- Subtopic: {subtopic}

Use this context:
\"\"\"
{context}
\"\"\"

Generate a structured lesson plan in JSON format, suitable for a PowerPoint presentation. Follow this structure:

{{{{
    "slides": [
      {{{{
        "type": "title",
        "title": "Temperature - Measure Heat",
        "subtitle": "Auto-generated Lesson Plan"
        "keyword": "Temperature" # keyword of slide
      }}}},
      {{{{
        "type": "content",
        "title": "Understanding Heat",
        "points": ["Heat is a form of energy", "It flows from hot to cold", "We measure it using thermometers"]
        "keyword": "Heat" # keyword of slide
      }}}},
      {{{{
        "type": "content",
        "title": "Measuring Temperature",
        "points": ["Thermometers use mercury or alcohol", "Readings are in Celsius or Fahrenheit"]
        "keyword": "Thermometer" # keyword of slide
      }}}},
      {{{{
        "type": "quiz",
        "title": "Quiz Time!",
        "quiz": {{{{
          "type": "mcq",
          "question": "What is used to measure temperature?",
          "options": ["Thermometer", "Barometer", "Hydrometer", "Speedometer"],
          "answer": "Thermometer"
        }}}}
      }}}}
    ]
}}}}
  

Instructions:
- Generate up to 3-5 content slides.
- Each slide should have a short title and 3-5 bullet points.
- End with a quiz slide using either MCQ or fill-in-the-blank.
- Return only the JSON object. Do NOT include any explanation, title, or commentary.
- Response must start with open curly bracket only.
- Make sure content in each slide should be complete and make sense.

"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a JSON-generating educational assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    content = res.json()["choices"][0]["message"]["content"]

    # Exxtracting ONLY and ONLY the JSON part.
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if not json_match:
        return {"error": "Failed to extract JSON", "raw": content}
    
    print("content from rag: "+content)

    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw": content}
