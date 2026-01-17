# 💼 Business Chat Agent

An AI-powered business intelligence tool that allows you to chat with your data using natural language queries. Upload CSV/Excel files and get instant insights powered by Google's Gemini AI.

## ✨ Features

- 📤 **File Upload**: Support for CSV and Excel files
- 💬 **Natural Language Queries**: Ask questions in plain English
- 🔄 **Real-time Streaming**: AI responses stream in real-time
- 📚 **Chat History**: Persistent conversation history
- 📊 **Quick Insights**: Pre-built queries for common analyses
- 🎨 **Beautiful UI**: Clean, modern interface built with Streamlit

## 🚀 Demo

[Add screenshot or GIF of your app here]

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/business-chat-agent.git
   cd business-chat-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your Google API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## 🎯 Usage

1. **Run the application**
   ```bash
   streamlit run app.py
   ```

2. **Upload your data**
   - Click "Browse files" in the sidebar
   - Upload a CSV or Excel file

3. **Start chatting**
   - Type your question in the chat input
   - Get AI-powered insights from your data

## 📊 Example Queries

- "What are the total sales last month?"
- "Show me the top 5 customers by revenue"
- "What trends can you identify in this data?"
- "Give me a summary of all numeric columns"

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

### Streamlit Cloud Deployment

1. Push your code to GitHub (without `.env` file)
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy your app
4. Add secrets in the Streamlit Cloud dashboard:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   ```

## 📁 Project Structure

```
business-chat-agent/
├── app.py              # Main Streamlit UI
├── backend.py          # Backend logic and AI agent
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🛡️ Security

- Never commit your `.env` file
- Keep your API keys secure
- Use `.gitignore` to prevent sensitive files from being uploaded

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Mr. Abdullah** - Developer
- **Miss Hooria** - Developer

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- Uses [LangChain](https://www.langchain.com/) for AI agent functionality

## 📧 Support

For support, email your_email@example.com or open an issue on GitHub.

---

Made with ❤️ by Abdullah & Hooria