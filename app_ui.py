import streamlit as st
import pandas as pd
from datetime import datetime
from backend import (
    read_file, 
    preprocess_data, 
    save_to_sql, 
    ai_sql_agent, 
    ask_question,
    init_chat_history_db,
    save_chat_to_history,
    load_chat_history,
    clear_all_chat_history
)

# Page configuration
st.set_page_config(
    page_title="Business Chat Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .timestamp {
        font-size: 0.75rem;
        color: #888;
        margin-top: 0.5rem;
    }
    .history-item {
        padding: 0.75rem;
        border-left: 3px solid #1f77b4;
        margin-bottom: 0.5rem;
        background-color: #f8f9fa;
        cursor: pointer;
        border-radius: 0.25rem;
    }
    .history-item:hover {
        background-color: #e9ecef;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False
if 'current_data' not in st.session_state:
    st.session_state.current_data = None

# Initialize chat history database
init_chat_history_db()

# Header
st.markdown('<div class="main-header">💼 Business Chat Agent</div>', unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.header("📊 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload your data file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file containing your business data"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            data, error = read_file(uploaded_file)
            
            if error:
                st.error(f"❌ Error: {error}")
            else:
                st.success("✅ File uploaded successfully!")
                
                # Preprocess and save data
                processed_data = preprocess_data(data)
                save_to_sql(processed_data)
                st.session_state.current_data = processed_data
                st.session_state.data_uploaded = True
                
                # Initialize agent
                if st.session_state.agent is None:
                    st.session_state.agent = ai_sql_agent()
                
                # Show data preview
                with st.expander("📋 Data Preview"):
                    st.dataframe(processed_data.head(10), use_container_width=True)
                    st.info(f"**Rows:** {len(processed_data)} | **Columns:** {len(processed_data.columns)}")
    
    st.divider()
    
    # History Management
    st.header("📚 Chat History")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True):
            if clear_all_chat_history():
                st.session_state.chat_history = []
                st.success("History cleared!")
                st.rerun()
            else:
                st.error("Failed to clear history")
    
    # Load and display history
    history_df = load_chat_history()
    
    if not history_df.empty:
        st.subheader(f"Recent Conversations")
        for idx, row in history_df.iterrows():
            with st.container():
                if st.button(
                    f"💬 {row['question'][:50]}...", 
                    key=f"hist_{row['id']}", 
                    use_container_width=True
                ):
                    st.session_state.chat_history = [
                        {"role": "user", "content": row['question'], "timestamp": row['timestamp']},
                        {"role": "assistant", "content": row['answer'], "timestamp": row['timestamp']}
                    ]
                    st.rerun()
                st.caption(f"🕒 {row['timestamp']}")
                st.divider()
    else:
        st.info("No history found")

# Main content area
if not st.session_state.data_uploaded:
    # Welcome screen
    st.info("👈 Please upload your business data file from the sidebar to get started")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📤 Upload Data")
        st.write("Upload CSV or Excel files with your business data")
    with col2:
        st.markdown("### 💬 Ask Questions")
        st.write("Get insights from your data using natural language")
    with col3:
        st.markdown("### 📊 Get Insights")
        st.write("Receive data-driven answers and recommendations")
    
else:
    # Chat interface
    st.subheader("💬 Ask Questions About Your Data")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                    <div class="timestamp">🕒 {message.get("timestamp", "")}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                    <div class="timestamp">🕒 {message.get("timestamp", "")}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Question input
    with st.form(key="question_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            question = st.text_input(
                "Your question:",
                placeholder="e.g., What are the total sales last month?",
                label_visibility="collapsed"
            )
        with col2:
            submit_button = st.form_submit_button("🚀 Ask", use_container_width=True)
    
    if submit_button and question:
        if st.session_state.agent is None:
            st.error("Agent not initialized. Please upload data first.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": question,
                "timestamp": timestamp
            })
            
            # Get response
            with st.spinner("🤔 Analyzing your data..."):
                try:
                    answer = ask_question(st.session_state.agent, question)
                    
                    # Add assistant message
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": timestamp
                    })
                    
                    # Save to history database
                    save_chat_to_history(question, answer)
                    
                except Exception as e:
                    error_msg = f"Error processing question: {str(e)}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": timestamp
                    })
                    st.error(error_msg)
            
            st.rerun()
    
    # Quick questions
    if st.session_state.current_data is not None:
        st.divider()
        st.subheader("💡 Quick Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Show summary statistics", use_container_width=True):
                question = "Give me a summary of all numeric columns in the data"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": question, 
                    "timestamp": timestamp
                })
                answer = ask_question(st.session_state.agent, question)
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer, 
                    "timestamp": timestamp
                })
                save_chat_to_history(question, answer)
                st.rerun()
        
        with col2:
            if st.button("🔝 Top performers", use_container_width=True):
                question = "Show me the top 5 records by value"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": question, 
                    "timestamp": timestamp
                })
                answer = ask_question(st.session_state.agent, question)
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer, 
                    "timestamp": timestamp
                })
                save_chat_to_history(question, answer)
                st.rerun()
        
        with col3:
            if st.button("📈 Trends analysis", use_container_width=True):
                question = "What trends can you identify in this data?"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": question, 
                    "timestamp": timestamp
                })
                answer = ask_question(st.session_state.agent, question)
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer, 
                    "timestamp": timestamp
                })
                save_chat_to_history(question, answer)
                st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>💼 <strong>Business Chat Agent</strong> | Powered by AI | Developed by <strong>Mr. Abdullah </strong></p>
    <p style='font-size: 0.875rem;'>Transform your data into actionable insights with natural language queries</p>
</div>
""", unsafe_allow_html=True)