from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from app.tools import get_tools
from dotenv import load_dotenv
import os

load_dotenv()

PROMPT = """You are a senior e-commerce data analyst. Be concise.

Tools:
{tools}

Tool names: {tool_names}

Tables:
- customers(customer_id, name, city, age, gender, joined_date)
- products(product_id, name, category, price, stock, rating)
- orders(order_id, customer_id, product_id, quantity, order_date, status, payment_method, revenue)

Rules:
- Keep thoughts to one sentence
- Always save charts to outputs/ with descriptive names
- End with a clean markdown report with numbers and insights
- For RFM: score recency/frequency/monetary each 1-4, label segments
- For cohort/trend: parse dates properly with strftime or pandas
- For funnel: count each order status stage
- For correlation: join tables then compute corr matrix as heatmap

Format:
Thought: one sentence
Action: tool name
Action Input: the input
Observation: result
Thought: I know the answer
Final Answer: markdown report with ## headers, tables, and bullet insights

Goal: {input}

{agent_scratchpad}"""


def get_agent():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=1024
    )
    tools = get_tools()
    prompt = PromptTemplate.from_template(PROMPT)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

def analyse(goal: str) -> str:
    try:
        result = get_agent().invoke({"input": goal})
        return result["output"]
    except Exception as e:
        return f"Error: {e}"