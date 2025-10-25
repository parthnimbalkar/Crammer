# pages/chat.py - Chat Interface with Minimalist Dark Theme
import streamlit as st
import requests

API_URL = "http://localhost:8000"

def show_chat_interface():
    """
    Render the chat interface with minimalist dark design
    """
    # Inject dark theme CSS for chat page
    st.markdown("""
    <style>
        /* Import Outfit font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        * {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Dark background */
        .stApp {
            background: #0f172a;
        }
        
        /* Chat container */
        .stChatFloatingInputContainer {
            background: #0f172a;
            border-top: 1px solid #334155;
        }
        
        /* Chat messages */
        [data-testid="stChatMessage"] {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        
        /* User message */
        [data-testid="stChatMessage"][data-testid*="user"] {
            background: #1e293b;
            border-color: #6366f1;
        }
        
        /* Assistant message */
        [data-testid="stChatMessage"][data-testid*="assistant"] {
            background: #1e293b;
            border-color: #334155;
        }
        
        /* Chat message content */
        .stChatMessage p {
            color: #e2e8f0;
            line-height: 1.6;
        }
        
        /* Chat input */
        .stChatInputContainer textarea {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            color: #e2e8f0 !important;
            border-radius: 8px !important;
        }
        
        .stChatInputContainer textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 1px #6366f1 !important;
        }
        
        .stChatInputContainer textarea::placeholder {
            color: #64748b !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: #1e293b;
            border: 1px solid #334155;
            color: #e2e8f0;
            padding: 0.5rem 1rem;
            font-size: 0.95rem;
            font-weight: 500;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background: #334155;
            border-color: #475569;
            transform: translateY(-1px);
        }
        
        /* Expander (sources) */
        .streamlit-expanderHeader {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #94a3b8 !important;
            font-size: 0.9rem;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #475569;
        }
        
        .streamlit-expanderContent {
            background: #0f172a;
            border: 1px solid #334155;
            border-top: none;
            color: #94a3b8;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #6366f1 !important;
        }
        
        /* Success/Error messages */
        .stSuccess, .stError, .stInfo {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #e2e8f0;
        }
        
        .stSuccess {
            border-left: 3px solid #10b981;
        }
        
        .stError {
            border-left: 3px solid #ef4444;
        }
        
        /* Captions */
        .stCaption {
            color: #64748b !important;
        }
        
        /* Dividers */
        hr {
            border: none;
            height: 1px;
            background: #334155;
            margin: 1.5rem 0;
        }
        
        /* Hide sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* Markdown text */
        .stMarkdown {
            color: #e2e8f0;
        }
        
        /* Headers in chat */
        h1, h2, h3, h4, h5, h6 {
            color: #e2e8f0 !important;
        }
        
        /* Code blocks in chat */
        code {
            background: #0f172a;
            color: #94a3b8;
            border: 1px solid #334155;
            border-radius: 4px;
            padding: 0.2rem 0.4rem;
        }
        
        pre code {
            display: block;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
        }
        
        /* Lists in chat */
        ul, ol {
            color: #e2e8f0;
        }
        
        li {
            color: #e2e8f0;
            margin-bottom: 0.5rem;
        }
        
        /* Strong/Bold text */
        strong {
            color: #f1f5f9;
            font-weight: 600;
        }
        
        /* Links */
        a {
            color: #6366f1;
        }
        
        a:hover {
            color: #818cf8;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize chat messages in session state if not exists
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and message.get("sources_used", 0) > 0:
                with st.expander(f"📚 Sources used: {message['sources_used']} chunks"):
                    st.caption("Response generated from your uploaded documents")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your study materials..."):
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare chat history
                    chat_history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.chat_messages[:-1]
                    ]
                    
                    # API call
                    response = requests.post(
                        f"{API_URL}/chat/",
                        json={
                            "message": prompt,
                            "chat_history": chat_history
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("success"):
                            data = result["data"]
                            answer = data["response"]
                            sources_used = data.get("sources_used", 0)
                            
                            # Display answer
                            st.markdown(answer)
                            
                            # Show sources
                            if sources_used > 0:
                                with st.expander(f"📚 Sources used: {sources_used} chunks"):
                                    st.caption("Response generated from your uploaded documents")
                            
                            # Add to history
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": answer,
                                "sources_used": sources_used
                            })
                        else:
                            st.error(f"Error: {result.get('error')}")
                    else:
                        st.error(f"API Error: {response.status_code}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Try a simpler question.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Is it running?")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Action buttons at bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔙 Back to Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    
    with col2:
        if len(st.session_state.chat_messages) > 0:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
    
    with col3:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()