import os
import csv
import sqlite3
from dotenv import load_dotenv
from google import genai
from langchain_core.documents import Document
from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma.vectorstores import Chroma


load_dotenv()
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

MAX_ROWS = 90
CSV_PATH = "data/raw/winemag-data-130k-v2-selected-columns.csv"
DB_PATH = "data/processed/wines_table.db"

def init_sqlite():
    os.makedirs("data/processed", exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE wines (id INTEGER PRIMARY KEY, country TEXT, description TEXT, 
        designation TEXT, points INTEGER, price REAL, province TEXT, region_1 TEXT,
        region_2 TEXT, taster_name TEXT)
    """)
    conn.commit()
    return conn


def ingest():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found. Create the file before the ingest")
    
    conn = init_sqlite()
    cursor = conn.cursor()
    documents = []

    with open(CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            if i >= MAX_ROWS:
                break
            
            cursor.execute("""
            INSERT INTO wines (country, description, designation, points, price, province, region_1, region_2, taster_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (row['country'], row['description'], row['designation'], row['points'], row['price'], row['province'], row['region_1'], row['region_2'], row['taster_name']))

            doc_content = (
                f"wine: {row['designation']}, {row['country']}, {row['province']}, {row['region_1']}, {row['region_2']}, {row['taster_name']}"
            )

            documents.append(
                Document(
                    page_content = doc_content,
                    metadata = { "id": row["id"], "designation": row["designation"]}
                )
            )

    conn.commit()
    conn.close()
    print("SQLite table created and data inserted successfully.")

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    Chroma.from_documents(documents, embeddings, persist_directory="data/processed/chroma_db")

    print("Chroma vector store created and persisted successfully.")



if __name__ == "__main__":
    ingest()