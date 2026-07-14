import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agent.tools import tools
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.0
)

memory = MemorySaver()

agent = create_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    system_prompt = """
You are a Wine Data Agent. Your job is to assist clients 
in finding and suggesting the correct wine models from the database.
Rules for your execution:
1. You have tools to query the local SQLite database. Always use them when asked about specific wine details.
2. If the user asks about a specific wine id or designation, call the appropriate query tool.
3. If the user provides specific requirements (country, designation, points, price, province, region_1, region_2, taster_name), call `query_by_specs`.
4. Be polite, precise, and reply based on the technical specifications retrieved.
"""
)