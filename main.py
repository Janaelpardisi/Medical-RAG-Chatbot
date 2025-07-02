import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# prepare gemini_api

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key = api_key)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# load data
df = pd.read_csv(r"F:\RAG_Medical_Chatbot\disease_description.csv")  
df = df.dropna(subset=["Disease", "Symptom_Description"])

# prepare base knowlege
knowledge_chunks = []
disease_names = []

for _, row in df.iterrows():
    disease = str(row["Disease"]).strip().lower()
    description = str(row["Symptom_Description"]).strip()
    chunk = f"Disease: {disease}\nSymptoms: {description}"
    knowledge_chunks.append(chunk)
    disease_names.append(disease)

# convert data to embedding
embedder = SentenceTransformer("all-MiniLM-L6-v2")
doc_embeddings = embedder.encode(knowledge_chunks)

# prepare faiss_index
index = faiss.IndexFlatL2(doc_embeddings[0].shape[0])
index.add(doc_embeddings)

# function for response to user
def ask_disease_bot(question):
    q_lower = question.strip().lower()

    
    if len(q_lower.split()) < 3:  
        return "❌ Sorry, I'm a medical assistant. Please ask me only about diseases or medical questions."

    # check if disease in dataset
    matched_diseases = [d for d in disease_names if d in q_lower]

    if matched_diseases:
        # use RAG
        q_embedding = embedder.encode([question])
        D, I = index.search(q_embedding, k=1)
        context = knowledge_chunks[I[0][0]]

        prompt = f"""
You are a helpful and professional medical assistant.
Below is disease information from a medical dataset:

{context}

Based on the information above, answer the user's question in a *detailed* and *informative* way.
Cover:
- Symptoms
- Causes
- Complications
- Treatments
- Any other important medical facts

Question: {question}
"""
    else:
        # if disease not in data use gemini
        prompt = f"""
You are a professional medical assistant.
Please answer the following medical question in *detailed, **clear, and **professional* language.
Explain:
- What the disease or symptom is
- Common causes
- Symptoms
- How it is diagnosed
- Complications
- Recommended treatments
Only answer if the question is clearly related to a medical condition or disease.
If it's not, respond with: "❌ Sorry, I'm a medical assistant. Please ask me only about diseases or medical questions."

Question: {question}
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {e}"

# generate response
#print("🩺 Welcome to the Medical Assistant Chatbot! Type 'exit' to quit.")
#while True:
    #user_input = input("You: ")
    #if user_input.strip().lower() == "exit":
        #break
    #response = ask_disease_bot(user_input)
    #print("🤖:", response, "\n")