import os
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_experimental.tools import PythonREPLTool
from sqlalchemy import create_engine

os.makedirs("outputs", exist_ok=True)

CHART_STYLE = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = ['#2196F3','#FF5722','#4CAF50','#FF9800','#9C27B0','#00BCD4','#F44336','#8BC34A']
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 120
})
"""

def get_tools():
    engine = create_engine("sqlite:///data/ecommerce.db")
    db = SQLDatabase(engine)

    sql_tool = QuerySQLDataBaseTool(db=db)
    sql_tool.name = "sql_query"
    sql_tool.description = (
        "Run a SQL query on the ecommerce database. "
        "Tables: customers, products, orders. "
        "Use this to fetch data, counts, aggregations and joins."
    )

    python_tool = PythonREPLTool()
    python_tool.name = "python_repl"
    python_tool.description = (
        "Execute Python code. Always start with this exact setup block:\n"
        f"{CHART_STYLE}\n"
        "Then use pandas for data, matplotlib/seaborn for charts. "
        "Save every chart with plt.savefig('outputs/chart_name.png', bbox_inches='tight'). "
        "Always call plt.close() after saving. "
        "Use the COLORS list for consistent palette."
    )

    return [sql_tool, python_tool]