import os
import sqlite3
from typing import Optional
from langchain_core.tools import tool
from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "wines_table.db")
CHROMA_DB_PATH = os.path.join(BASE_DIR, "data", "processed", "chroma_db")
TABLE_NAME = "wines"

@tool
def query_by_id(id: str) -> str:
    """
    Consults the database to retrieve all technical specifications of a specific wine 
    using its exact id. Use this tool when the user mentions a specific id number.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    clean_id = id.strip()

    query = f'SELECT * FROM {TABLE_NAME} WHERE id LIKE ?'
    cursor.execute(query, (f"%{clean_id}%",))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No wine found for id: {id}"

    return str([dict(row) for row in rows])


@tool
def query_by_designation(designation: str) -> str:
    """
    Consults the database to retrieve all technical specifications of a specific wine 
    using its exact designation. Use this tool when the user mentions a specific designation.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    clean_designation = designation.strip()

    query = f'SELECT * FROM {TABLE_NAME} WHERE designation LIKE ?'
    cursor.execute(query, (f"%{clean_designation}%",))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No wine found for designation: {designation}"

    return str([dict(row) for row in rows])

@tool
def query_by_specs(country: Optional[str] = None,
                   designation: Optional[str] = None,
                   points: Optional[int] = None,
                   price: Optional[float] = None,
                   province: Optional[str] = None,
                   region_1: Optional[str] = None,
                   region_2: Optional[str] = None,
                   taster_name: Optional[str] = None
            ) -> str:
    """
    Search and filter wines based on various specifications such as country, designation, points, price, province, region_1, region_2, and taster_name.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    query = f'SELECT * FROM {TABLE_NAME} WHERE 1=1'
    params = []

    if country:
        query += ' AND country LIKE ?'
        params.append(f"%{country}%")

    if designation:
        query += ' AND designation LIKE ?'
        params.append(f"%{designation}%")

    if points is not None:
        query += ' AND points = ?'
        params.append(points)

    if price is not None:
        query += ' AND price = ?'
        params.append(price)

    if province:
        query += ' AND province LIKE ?'
        params.append(f"%{province}%")

    if region_1:
        query += ' AND region_1 LIKE ?'
        params.append(f"%{region_1}%")

    if region_2:
        query += ' AND region_2 LIKE ?'
        params.append(f"%{region_2}%")

    if taster_name:
        query += ' AND taster_name LIKE ?'
        params.append(f"%{taster_name}%")

    query += "LIMIT 3"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No wine found for specs"

    return str([dict(row) for row in rows])


tools = [query_by_id, query_by_designation, query_by_specs]