from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from app.tools import get_tools
from dotenv import load_dotenv
import os
import re

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
- Pass ONLY raw SQL to sql_query — NO backticks, NO markdown fences
- Always save charts to outputs/ with descriptive names
- End with a clean markdown report with numbers and insights
- For RFM: score recency/frequency/monetary each 1-4, label segments
- For funnel: count each order status stage
- For correlation: join tables then compute corr matrix as heatmap
- Write EITHER an Action OR a Final Answer — NEVER both in the same response
- Once you write Final Answer, stop immediately — do not add any Action after it

Format strictly:
Thought: one sentence
Action: tool name
Action Input: the input
Observation: result
...repeat as needed...
Thought: I have enough to write the report
Final Answer: your markdown report here

Goal: {input}

{agent_scratchpad}"""


def extract_final_answer(text: str):
    """Rescue Final Answer from OUTPUT_PARSING_FAILURE responses."""
    match = re.search(
        r'Final Answer\s*:\s*(.*?)(?:For troubleshooting|$)',
        text, re.DOTALL | re.IGNORECASE
    )
    if match:
        answer = match.group(1).strip()
        if len(answer) > 20:
            return answer
    return None


def build_executor(model: str) -> AgentExecutor:
    llm = ChatGroq(
        model=model,
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
        max_iterations=8,
        handle_parsing_errors=True
    )


def analyse(goal: str) -> str:
    for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            print(f"[agent] trying {model}...")
            executor = build_executor(model)
            result = executor.invoke({"input": goal})
            output = result["output"]

            # agent returned answer but parsing also failed midway
            # the answer is buried after OUTPUT_PARSING_FAILURE text
            if "OUTPUT_PARSING_FAILURE" in output:
                rescued = extract_final_answer(output)
                if rescued:
                    print(f"[agent] rescued answer from parsing failure")
                    return rescued
                print(f"[agent] parsing failed, no rescuable answer — trying next model")
                continue

            print(f"[agent] success with {model}")
            return output

        except Exception as e:
            err_str = str(e).lower()
            cause_str = str(getattr(e, '__cause__', '')).lower()
            combined = err_str + cause_str

            is_rate_limit = any(x in combined for x in [
                "429", "rate_limit", "rate limit",
                "tokens per day", "tpd", "please try again",
                "quota", "resource_exhausted"
            ])

            if is_rate_limit:
                print(f"[fallback] {model} rate limited → switching model")
                continue
            else:
                return f"Error: {e}"

    return "Both models hit the daily limit. Free tier resets in 24 hours."