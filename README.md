# 🎓 Crammer - AI-Powered Study Assistant

> Transform your study materials into an interactive learning experience with RAG-powered chat and flashcards

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.50+-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Crammer is an intelligent study assistant that uses Retrieval-Augmented Generation (RAG) to help students learn from their own study materials. Upload your documents (PDF, DOCX, TXT), and Crammer creates an interactive learning environment with AI-powered chat and automatically generated flashcards.

**Live Demo**: [crammer.streamlit.app](#) 

---

## ✨ Features

### 🤖 **Smart Chat Interface**
- Ask questions about your uploaded documents
- Get detailed, contextual explanations grounded in your materials
- Conversational AI that understands follow-up questions
- Sources tracked and cited from your documents

### 🗂️ **AI-Generated Flashcards**
- Automatically creates flashcards from your content
- Interactive flip cards for active recall
- Track your progress (mark cards as known/unknown)
- Customizable number of cards (5-30)

### 📚 **Document Support**
- Upload multiple documents simultaneously
- Supports PDF, DOCX, and TXT formats
- Intelligent chunking (1000 chars, 200 overlap) for optimal retrieval
- Semantic search using Pinecone vector database

### 🎨 **Modern Dark UI**
- Clean, minimalist dark theme (navy + indigo palette)
- Eye-soothing colors designed for long study sessions
- Responsive design (desktop and mobile)
- Distraction-free learning experience with Outfit font

---

## 🛠️ Tech Stack

### **Frontend**
- **Streamlit 1.50.0** - Interactive web interface
- **Custom CSS** - Minimalist dark theme with Outfit font
- **Streamlit Cloud** - Deployment platform

### **Backend**
- **FastAPI 0.119.0** - High-performance REST API
- **Uvicorn** - ASGI server
- **Python 3.11+** - Core application logic

### **AI & ML**
- **Groq API** - Fast LLM inference (Llama 3.1 8B Instant)
- **LangChain** - RAG orchestration framework
  - `langchain-core 1.0.0`
  - `langchain-groq 1.0.0`
  - `langchain-text-splitters 1.0.0`
- **Pinecone Inference API** - Embeddings generation
  - Model: `llama-text-embed-v2` (1024 dimensions)
  - No local embedding models required!

### **Vector Database**
- **Pinecone 5.0.0** - Serverless vector storage and similarity search
- Index: `crammer` (1024-dimensional vectors)

### **Document Processing**
- **PyPDF2 3.0.1** - PDF text extraction
- **python-docx 1.2.0** - DOCX parsing
- **Unstructured 0.18.15** - Multi-format document processing
- **LangChain Text Splitters** - Intelligent chunking

---

## 🏗️ Architecture

Crammer uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware responses:

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│                    (Documents / Questions)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING                       │
│  • Parse files (PDF, DOCX, TXT)                             │
│  • Split into chunks (1000 chars, 200 overlap)              │
│  • Generate embeddings via Pinecone Inference API           │
│    (llama-text-embed-v2, 1024-dim)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      PINECONE STORAGE                       │
│  • Store vectors in 'crammer' index                         │
│  • Serverless, scalable vector database                     │
│  • Metadata: text, source, chunk_index                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RETRIEVAL (Query Time)                   │
│  • User asks question                                       │
│  • Query → Embedding (Pinecone Inference API)               │
│  • Similarity search → Retrieve top k chunks                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   GENERATION (Groq LLM)                     │
│  • Context + Query → Groq API (Llama 3.1 8B)                │
│  • Generate contextual response                             │
│  • Return to user with source citations                     │
└─────────────────────────────────────────────────────────────┘
```

### **Key Advantages:**
- **No local embeddings needed** - Pinecone Inference API handles everything
- **Fast retrieval** - Pinecone's optimized vector search
- **Scalable** - Serverless architecture handles any workload
- **Accurate** - Responses grounded in your actual documents

---

## 📥 Installation

### **Prerequisites**
- Python 3.11 or higher
- pip (Python package manager)
- Git


### **Step 1: Clone the Repository**
```bash
git clone https://github.com/yourusername/crammer-prepmate.git
cd crammer-prepmate
```

### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### **Step 3: Install Dependencies**

**For Backend:**
```bash
cd prepmate
pip install -r backend-requirements.txt
```

**For Frontend:**
```bash
pip install -r requirements.txt
```

### **Step 4: Set Up Pinecone Index**

1. **Create a Pinecone account** at [pinecone.io](https://www.pinecone.io/)
2. **Create a new index** with these settings:
   - Name: `crammer`
   - Dimensions: `1024`
   - Metric: `cosine`
   - Cloud: `AWS`
   - Region: `us-east-1` (or your preferred region)

### **Step 5: Get API Keys**

**Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up / Log in
3. Create a new API key
4. Copy the key

**Pinecone API Key:**
1. In Pinecone dashboard, go to **API Keys**
2. Copy your API key

### **Step 6: Set Up Environment Variables**

Create a `.env` file in the `prepmate/` directory:

```bash
cd prepmate
touch .env
```

Add the following to your `.env` file:
```env
# Groq API
GROQ_API_KEY=your_groq_api_key_here

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here

# API URL (for local development)
API_URL=http://localhost:8000
```

---

## 🚀 Usage

### **Local Development**

**Start the Backend (Terminal 1):**
```bash
cd prepmate
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

**Start the Frontend (Terminal 2):**
```bash
# Make sure you're in the project root
streamlit run prepmate/app.py
```

The app will open in your browser at `http://localhost:8501`

### **Using Crammer**

1. **Upload Documents**
   - Click on the home page to select files
   - Choose PDF, DOCX, or TXT files (multiple allowed)
   - Click "Upload & Process"
   - Wait for processing (documents → chunks → vectors)
   - View metrics: Files, Chunks, Vectors

2. **Chat Mode**
   - Click "Start Chatting"
   - Ask questions about your materials
   - Get AI responses with source citations
   - Have follow-up conversations
   - Chat history is preserved during session

3. **Flashcards Mode**
   - Click "Create Flashcards"
   - Enter a topic (or leave blank for general cards)
   - Specify number of cards (5-30, default: 10)
   - Click "Generate Flashcards"
   - Review cards: flip, mark as known, track progress
   - Navigate with Previous/Next or jump to specific cards

---

## 📂 Project Structure

```
crammer-prepmate/
│
├── .devcontainer/
│   └── devcontainer.json          # Dev container configuration
│
├── prepmate/                       # Main application directory
│   │
│   ├── .streamlit/
│   │   └── config.toml            # Streamlit theme configuration
│   │
│   ├── pages/                     # Streamlit pages
│   │   ├── chat.py               # Chat interface
│   │   └── flashcards.py         # Flashcards interface
│   │
│   ├── app.py                     # Main Streamlit app (home page)
│   ├── main.py                    # FastAPI backend server
│   ├── rag_engine.py              # Core RAG functionality
│   ├── prompts.py                 # LLM prompts for different modes
│   ├── converter.py               # Document processing & Pinecone upload
│   ├── upload.py                  # Upload endpoint logic
│   ├── clean_install.py           # Dependency installation script
│   │
│   ├── requirements.txt           # Frontend dependencies
│   ├── backend-requirements.txt   # Backend dependencies
│   ├── .env                       # Environment variables (create this)
│   └── procfile                   # Deployment configuration
│
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git attributes
└── README.md                      # This file
```

### **Key Files Explained**

**Frontend:**
- `prepmate/app.py` - Main entry point, handles page routing and upload UI
- `prepmate/pages/chat.py` - Chat interface with conversation history
- `prepmate/pages/flashcards.py` - Flashcard generation and review interface
- `prepmate/.streamlit/config.toml` - Theme colors and configuration

**Backend:**
- `prepmate/main.py` - FastAPI app with endpoints (upload, chat, flashcards, clear)
- `prepmate/rag_engine.py` - RAGTutor class with Pinecone Inference integration
- `prepmate/converter.py` - Document processing and vector storage
- `prepmate/upload.py` - File upload router
- `prepmate/prompts.py` - Carefully crafted prompts for AI responses

**Configuration:**
- `.env` - API keys and configuration (you create this)
- `prepmate/backend-requirements.txt` - Python dependencies for backend
- `prepmate/requirements.txt` - Python dependencies for frontend

---

## ⚙️ Configuration

### **Environment Variables**

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Your Groq API key | ✅ Yes | `gsk_...` |
| `PINECONE_API_KEY` | Your Pinecone API key | ✅ Yes | `pcsk_...` |
| `API_URL` | Backend URL | ✅ Yes | `http://localhost:8000` |

### **RAG Configuration**

**In `rag_engine.py`:**

```python
# Number of chunks to retrieve (k values)
chat()               # k=5  - Conversational context
answer_question()    # k=3  - Focused answers
teach()              # k=5  - Comprehensive teaching
generate_flashcards() # k=8 - Diverse flashcard content
```

**Embedding Model:**
- Model: `llama-text-embed-v2` (Pinecone Inference API)
- Dimensions: 1024
- Input types: `passage` (for documents), `query` (for search)

**Document Processing:**
```python
# In converter.py
chunk_size = 1000       # Characters per chunk
chunk_overlap = 200     # Overlap between chunks
batch_size = 96         # Chunks per embedding batch
```

**LLM Settings:**
```python
# In rag_engine.py
model = "llama-3.1-8b-instant"  # Groq model
temperature = 0.7                # Creativity level (0-1)
```

### **Pinecone Index Settings**

When creating your index:
- **Name**: `crammer` (must match in code)
- **Dimensions**: `1024` (llama-text-embed-v2)
- **Metric**: `cosine`
- **Cloud**: AWS
- **Region**: us-east-1 (or your choice)
- **Plan**: Free tier (100K vectors) or paid

---

## 🎨 Customization

### **Change UI Colors**

Edit the CSS in `prepmate/app.py`:

```css
/* Main background */
background: #0f172a;  /* Deep navy */

/* Cards */
background: #1e293b;  /* Dark blue-gray */

/* Accent color */
color: #6366f1;  /* Soft indigo */
```

Or modify `prepmate/.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#6366f1"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#e2e8f0"
```

### **Change Fonts**

In `app.py` CSS section:
```css
@import url('https://fonts.googleapis.com/css2?family=YourFont:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'YourFont', sans-serif;
}
```

### **Modify Prompts**

Edit `prepmate/prompts.py` to customize AI behavior:
- `TUTOR_SYSTEM_PROMPT` - Overall AI personality
- `CHAT_PROMPT` - For conversations
- `TEACHING_PROMPT` - For explanations
- `QA_PROMPT` - For direct questions
- `FLASHCARD_PROMPT` - For flashcard generation

### **Adjust Chunk Size**

In `prepmate/converter.py`:
```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    # Modify chunk_size and overlap values
```

Larger chunks = more context per chunk, fewer total chunks
Smaller chunks = more precise retrieval, more chunks

---

## 🚀 Deployment

### **Streamlit Cloud**

1. **Push to GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Select `prepmate/app.py` as main file
   - Add secrets in Streamlit dashboard:
     ```toml
     API_URL = "your-backend-url"
     GROQ_API_KEY = "your-groq-key"
     PINECONE_API_KEY = "your-pinecone-key"
     ```

3. **Deploy Backend Separately:**
   - Options: Railway, Render, Heroku, DigitalOcean
   - Use `prepmate/procfile` for configuration
   - Set environment variables on platform
   - Update `API_URL` in Streamlit secrets

### **Docker (Optional)**

Create `Dockerfile` in `prepmate/`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend-requirements.txt .
RUN pip install -r backend-requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t crammer-backend .
docker run -p 8000:8000 --env-file .env crammer-backend
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

### **Ways to Contribute**
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🎨 Enhance UI/UX
- 🔧 Fix issues
- ⚡ Optimize performance

### **Development Process**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly
5. Commit (`git commit -m 'Add AmazingFeature'`)
6. Push (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### **Code Guidelines**
- Follow PEP 8 for Python
- Use type hints where appropriate
- Add docstrings to functions
- Write meaningful commit messages
- Test before submitting PR

---

## 🗺️ Roadmap

### **Current (v1.0)** ✅
- Document upload (PDF, DOCX, TXT)
- RAG-powered chat with Pinecone Inference
- AI flashcard generation
- Minimalist dark UI
- Progress tracking
- Streamlit Cloud deployment

### **Coming Soon (v1.1)** 🔄
- Quiz generation feature
- Export flashcards (CSV, Anki)
- Document summary generation
- Multiple document collections
- Study statistics dashboard
- Better error handling

### **Future (v2.0)** 🔮
- Spaced repetition algorithm
- Voice input/output
- Collaborative study sessions
- Mobile app (React Native)
- Google Drive/Dropbox integration
- Image OCR support (scanned notes)
- Offline mode with local LLM

### **Known Issues** 🐛
- Large PDFs (50+ pages) may timeout
- Flashcard parsing rarely needs retry
- Chat history not persisted after browser close
- First query after upload is slower (index initialization)

---

## 🐛 Troubleshooting

### **Backend won't start**
```bash
# Check if port 8000 is in use
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Verify environment
cd prepmate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GROQ:', os.getenv('GROQ_API_KEY')[:10])"
```

### **Pinecone errors**
- Verify API key in `.env`
- Check index name is `crammer`
- Ensure index dimensions = 1024
- Verify serverless index is created
- Check Pinecone dashboard: [app.pinecone.io](https://app.pinecone.io)

### **Groq API errors**
- Check API key validity
- Verify rate limits (free: 30 req/min)
- Try regenerating key
- Check [console.groq.com](https://console.groq.com/)

### **No vectors uploaded**
```bash
cd prepmate
python -c "from pinecone import Pinecone; import os; from dotenv import load_dotenv; load_dotenv(); pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY')); print(pc.Index('crammer').describe_index_stats())"
```

### **Import errors**
```bash
# Clean install
cd prepmate
python clean_install.py
```

### **Frontend can't connect to backend**
- Verify backend is running on port 8000
- Check `API_URL` in `.env` or Streamlit secrets
- Test: `curl http://localhost:8000/health`

---

## 💰 Cost & Limits

### **Free Tier Limits**

**Groq (Free):**
- 30 requests per minute
- 14,400 requests per day
- Perfect for development and personal use

**Pinecone (Free):**
- 1 free serverless index
- 100,000 vectors
- Good for ~100-200 documents

**Streamlit Cloud (Free):**
- Unlimited public apps
- 1GB resources per app
- Community support

### **When to Upgrade**

**Groq ($)** - When you need:
- Higher rate limits (>30 req/min)
- Guaranteed uptime
- Priority support

**Pinecone ($)** - When you need:
- >100K vectors (~200+ documents)
- Multiple indexes
- Higher performance
- Starting at $70/month

---

## 📄 License

MIT License - See LICENSE file for details

```
Copyright (c) 2024 Crammer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

### **Technologies**
- [Groq](https://groq.com/) - Lightning-fast LLM inference
- [Pinecone](https://www.pinecone.io/) - Vector database with Inference API
- [Streamlit](https://streamlit.io/) - Python web app framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [LangChain](https://langchain.com/) - LLM orchestration

### **Models**
- **Llama 3.1 8B Instant** (Meta) - Chat completions via Groq
- **llama-text-embed-v2** (Pinecone) - Text embeddings

### **Inspiration**
- RAG architecture from modern AI research
- Study app patterns from Quizlet, Anki, RemNote

---

## 💬 Support

### **Get Help**
- 🐛 [Report Issues](https://github.com/yourusername/crammer-prepmate/issues)
- 💡 [Feature Requests](https://github.com/yourusername/crammer-prepmate/issues/new?labels=enhancement)
- 📧 Email: support@crammer.app *(if applicable)*

### **Community**
- ⭐ Star this repo if helpful!
- 🔔 Watch for updates
- 🍴 Fork to customize

---

## 🎓 About Crammer

Crammer was built to make studying more effective through AI. By combining RAG with your personal study materials, we create a customized learning experience that adapts to your needs.

**Built for students, by students** 📚

---

<div align="center">

**[⬆ Back to Top](#-crammer---ai-powered-study-assistant)**

Made with 💙 by Parth Nimbalkar

</div>
