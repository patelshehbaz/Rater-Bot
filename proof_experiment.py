import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import os
import csv
from pathlib import Path

# Load .env file
load_dotenv()


# --- Step 1: Load and Prepare HTS JSON Data ---
def load_hts_data(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = []
    for entry in data:
        htsno = entry.get("htsno", "N/A")
        desc = entry.get("description", "")
        general = entry.get("general", "")
        special = entry.get("special", "")
        other = entry.get("other", "")
        
        full_text = f"HTS Number: {htsno}\nDescription: {desc}\nGeneral Rate: {general}\nSpecial Rate: {special}\nOther Rate: {other}"
        documents.append(Document(page_content=full_text))
    
    return documents

# --- Step 2: Chunk the Text ---
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    return splitter.split_documents(documents)

# --- Step 3: Embed and Index with FAISS ---
def build_vector_store(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
    return vectorstore

# --- Step 4: Set up RAG Pipeline ---
def setup_qa_pipeline(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = OpenAI(temperature=0)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa

def save_proof_as_image(text, file_name="proof.png"):
    font = ImageFont.load_default()
    lines = text.split("\n")
    # create a temporary image just to calculate text width
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    width = max(draw.textlength(line, font=font) for line in lines) + 20
    height = len(lines) * 15 + 20

    img = Image.new("RGB", (int(width), height), color="white")
    d = ImageDraw.Draw(img)
    
    y = 10
    for line in lines:
        d.text((10, y), line, font=font, fill="black")
        y += 15

    img.save(file_name)
    print(f"Screenshot saved as {file_name}")

# --- Step 5: Main Execution ---
def main():
    json_path = "htsdata (85).json"
    
    print("Loading and processing HTS data...")
    documents = load_hts_data(json_path)
    chunks = split_documents(documents)
    
    print("Building FAISS index...")
    vectorstore = build_vector_store(chunks)
    
    print("Setting up QA pipeline...")
    qa_pipeline = setup_qa_pipeline(vectorstore)

    question = "What is the HTS number for LED lamps with a cap designed to be directly installed into luminaires?"
    print(f"\nQuestion: {question}")
    response = qa_pipeline.invoke({"query": question})
    print("\nAnswer:", response["result"])

    # Show retrieved source chunks (proof)
    print("\n--- Source Document(s) Used ---")
    for i, doc in enumerate(response["source_documents"]):
        print(f"\n[Document {i+1}]\n{doc.page_content}")

    # Add this part for screenshot
    proof_text = "\n".join(doc.page_content for doc in response["source_documents"])
    save_proof_as_image(proof_text)


if __name__ == "__main__":
    main()