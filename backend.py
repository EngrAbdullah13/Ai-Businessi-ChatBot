import pandas as pd
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent

# Load environment variables from .env file
load_dotenv()


# ==================== FILE OPERATIONS ====================

def read_file(uploaded_file):
    """Read CSV or Excel file and return DataFrame"""
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file format. Use CSV or Excel."
        
        if data.empty:
            return None, "File is empty!"
        
        return data, None
    except Exception as e:
        return None, str(e)


def preprocess_data(df):
    """Preprocess DataFrame: clean column names, remove nulls, convert types"""
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df = df.dropna()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)
    print("Preprocessing done")    
    return df


# ==================== USER DATA DATABASE ====================

def save_to_sql(df, db_path="user_data.db"):
    """Save DataFrame to SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql("uploaded_data", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Data saved to {db_path}")
    except Exception as e:
        print(f"Error saving data to SQL: {e}")
        raise


# ==================== CHAT HISTORY DATABASE ====================

def init_chat_history_db(db_path="chat_history.db"):
    """Initialize chat history database with required table"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      session_name TEXT,
                      timestamp TEXT,
                      question TEXT,
                      answer TEXT)''')
        conn.commit()
        conn.close()
        print(f"Chat history database initialized: {db_path}")
    except Exception as e:
        print(f"Error initializing chat history database: {e}")
        raise


def save_chat_to_history(question, answer, session_name="Default Session", db_path="chat_history.db"):
    """Save a chat interaction to history database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT INTO chat_sessions (session_name, timestamp, question, answer) VALUES (?, ?, ?, ?)",
            (session_name, timestamp, question, answer)
        )
        conn.commit()
        conn.close()
        print(f"Chat saved to history at {timestamp}")
        return True
    except Exception as e:
        print(f"Error saving chat to history: {e}")
        return False


def load_chat_history(db_path="chat_history.db"):
    """Load all chat history from database"""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT * FROM chat_sessions ORDER BY timestamp DESC", 
            conn
        )
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return pd.DataFrame()


def clear_all_chat_history(db_path="chat_history.db"):
    """Clear all chat history from database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM chat_sessions")
        conn.commit()
        conn.close()
        print("All chat history cleared")
        return True
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return False


# ==================== AI AGENT ====================

def ai_sql_agent(db_path="user_data.db"):
    """Initialize and return AI SQL agent"""
    # Get API key from environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found! Please set it in your .env file or environment variables."
        )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=api_key
    )

    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    agent = create_agent(
        llm,
        toolkit.get_tools(),
        system_prompt="""You are an AI Data Analyst connected to a SQL database.

STRICT RULES:
1. You MUST always inspect the database schema first.
2. You MUST identify and understand the table name(s) and column names before generating any SQL.
3. You MUST infer column names by meaning, not by exact wording.
4. You MUST always generate and execute SQL queries before answering.
5. You MUST base your answers ONLY on the SQL query results.
6. Never hallucinate or use general knowledge.

PROFESSIONAL OUTPUT FORMAT:
Instead of just listing raw data, you MUST:

1. START with a brief executive summary (2-3 sentences)
2. HIGHLIGHT key insights and patterns you found
3. MENTION specific numbers that stand out (highest, lowest, averages)
4. PROVIDE actionable insights or observations
5. Keep the tone professional and analytical

EXAMPLE OF GOOD OUTPUT:
"Based on the sales data analysis, California shows strong performance with total sales of $1.2M across the period, peaking in August 2022 at $75,461. The trend indicates seasonal variations with higher sales during summer months (June-August) and year-end periods (December). Florida demonstrates more consistent performance at $950K total, with notable peaks in November 2021 ($76,955) and June 2024 ($57,047).

Key Insights:
• California: 22% year-over-year growth in 2023
• Florida: More stable monthly distribution
• Both states show strong Q2 and Q4 performance
• Recommendation: Focus marketing efforts on identified peak periods"

REMEMBER: 
- Always provide context and insights
- Highlight trends and patterns
- Make the data actionable
- Be concise but informative
"""     
    )
    return agent


def ask_question(agent, question):
    """Ask a question to the AI agent and return the answer"""
    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )

        result = response["messages"][-1].content

        # Gemini-safe handling
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    return item.get("text") or item.get("content") or ""
            return ""

        return result
    except Exception as e:
        print(f"Error asking question: {e}")
        return f"Error processing question: {str(e)}"