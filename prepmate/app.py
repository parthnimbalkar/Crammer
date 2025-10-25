import os
import streamlit as st
import requests
from pages.chat import show_chat_interface
from pages.flashcards import show_flashcards_interface

if hasattr(st, 'secrets') and 'API_URL' in st.secrets:
    API_URL = st.secrets["API_URL"]
else:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Crammer - AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimalist Dark Theme CSS
st.markdown("""
<style>
    /* Import Clean Font - Outfit */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Dark Background */
    .stApp {
        background: #0f172a;
    }
    
    /* Main Container */
    .block-container {
        padding-top: 3rem;
        max-width: 1100px;
    }
    
    /* Header Section */
    .header-section {
        text-align: center;
        margin-bottom: 4rem;
    }
    
    .app-title {
        font-size: 3.5rem;
        font-weight: 300;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
    }
    
    /* Upload Section */
    .upload-section {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 3rem;
        margin-bottom: 3rem;
    }
    
    .upload-title {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .upload-desc {
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: #0f172a;
        border: 2px dashed #475569;
        border-radius: 8px;
        padding: 2rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #64748b;
    }
    
    [data-testid="stFileUploader"] label {
        color: #cbd5e1 !important;
    }
    
    /* Mode Cards - Clean & Minimal */
    .mode-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .mode-card:hover {
        border-color: #6366f1;
        background: #232e42;
        transform: translateY(-2px);
    }
    
    .mode-icon {
        font-size: 3rem;
        margin-bottom: 1.25rem;
        opacity: 0.9;
    }
    
    .mode-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.75rem;
    }
    
    .mode-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Buttons - Minimal Style */
    .stButton>button {
        width: 100%;
        background: #6366f1;
        color: white;
        padding: 0.875rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        border: none;
        border-radius: 8px;
        transition: all 0.2s ease;
        letter-spacing: 0.3px;
    }
    
    .stButton>button:hover {
        background: #4f46e5;
        transform: translateY(-1px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Secondary Buttons */
    .stButton button[kind="secondary"] {
        background: transparent;
        border: 1px solid #475569;
        color: #cbd5e1;
    }
    
    .stButton button[kind="secondary"]:hover {
        background: #1e293b;
        border-color: #64748b;
    }
    
    /* Metrics - Clean Design */
    [data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 8px;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 600;
        font-size: 2rem !important;
    }
    
    /* File Cards */
    .file-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    
    .file-card:hover {
        border-color: #475569;
    }
    
    .file-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    .file-name {
        color: #e2e8f0;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
        word-break: break-word;
    }
    
    .file-size {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    /* Feature Section */
    .feature-section {
        margin-top: 3rem;
    }
    
    .section-title {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 2rem;
        height: 100%;
        transition: border-color 0.2s ease;
    }
    
    .feature-card:hover {
        border-color: #475569;
    }
    
    .feature-card h4 {
        color: #f1f5f9;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    .feature-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-card li {
        color: #94a3b8;
        margin-bottom: 0.75rem;
        padding-left: 1.5rem;
        position: relative;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .feature-card li::before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #6366f1;
        font-weight: bold;
    }
    
    /* Success/Error/Info Messages */
    .stSuccess, .stError, .stInfo, .stWarning {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 3px solid #6366f1;
        border-radius: 8px;
        color: #cbd5e1;
    }
    
    .stSuccess {
        border-left-color: #10b981;
    }
    
    .stError {
        border-left-color: #ef4444;
    }
    
    .stInfo {
        border-left-color: #3b82f6;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: #334155;
        margin: 2.5rem 0;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
        font-weight: 600;
    }
    
    h3 {
        font-size: 1.75rem;
        margin-bottom: 1.5rem;
    }
    
    h4 {
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* Text colors */
    .stMarkdown, p, span, div {
        color: #cbd5e1;
    }
    
    /* List items */
    li {
        color: #94a3b8;
    }
    
    strong {
        color: #f1f5f9;
        font-weight: 600;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
    
    /* Tooltips */
    [data-testid="stTooltipIcon"] {
        color: #64748b;
    }
    
    /* Action Buttons Row */
    .action-row {
        margin-bottom: 2rem;
    }
    
    /* Spacing utilities */
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    .mb-4 { margin-bottom: 2rem; }
    
    /* Responsive */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2.5rem;
        }
        
        .mode-card {
            height: auto;
            min-height: 200px;
        }
        
        .upload-section {
            padding: 2rem 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# ========== PAGE ROUTING ==========
if st.session_state.current_page == "chat":
    show_chat_interface()

elif st.session_state.current_page == "flashcards":
    show_flashcards_interface()

else:
    # ========== HOME PAGE ==========
    
    # Header
    st.markdown("""
    <div class="header-section">
        <h1 class="app-title">Crammer</h1>
        <p class="app-subtitle">Your AI-powered study companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== UPLOAD SECTION (show if not uploaded) ==========
    if not st.session_state.uploaded:
        st.markdown("""
        <div class="upload-section">
            <h3 class="upload-title">Get Started</h3>
            <p class="upload-desc">Upload your study materials to begin learning</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="Select one or more documents",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown('<div class="mb-3"></div>', unsafe_allow_html=True)
            st.markdown("#### Selected Files")
            
            cols = st.columns(min(len(uploaded_files), 3))
            for idx, file in enumerate(uploaded_files):
                file_size = len(file.getvalue()) / 1024
                with cols[idx % len(cols)]:
                    st.markdown(f"""
                    <div class="file-card">
                        <div class="file-icon">📄</div>
                        <div class="file-name">{file.name}</div>
                        <div class="file-size">{file_size:.1f} KB</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('<div class="mb-2"></div>', unsafe_allow_html=True)
            
            if st.button("Upload & Process", type="primary"):
                with st.spinner("Processing documents..."):
                    try:
                        files = [
                            ("files", (file.name, file.getvalue(), file.type))
                            for file in uploaded_files
                        ]
                        
                        response = requests.post(
                            f"{API_URL}/upload/multiple",
                            files=files,
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✓ Documents processed successfully")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Files", result.get("files_processed", 0))
                            with col2:
                                st.metric("Chunks", result.get("chunks_created", 0))
                            with col3:
                                st.metric("Vectors", result.get("total_vectors_in_index", 0))
                            
                            st.session_state.uploaded = True
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"Upload failed: {response.status_code}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("Select files to get started")
    
    # ========== MODE SELECTION (show if uploaded) ==========
    else:
        # Action buttons
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col3:
            if st.button("Upload More", key="upload_more"):
                st.session_state.uploaded = False
                st.rerun()
        
        with col4:
            if st.button("Clear All", key="clear_all"):
                with st.spinner("Clearing..."):
                    try:
                        response = requests.post(f"{API_URL}/clear", timeout=30)
                        result = response.json()
                        
                        if result.get("success"):
                            st.success("✓ Documents cleared")
                            st.session_state.uploaded = False
                            if "chat_messages" in st.session_state:
                                st.session_state.chat_messages = []
                            if "flashcards" in st.session_state:
                                st.session_state.flashcards = []
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('error')}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown('<div class="mb-4"></div>', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Choose Your Study Mode</h3>', unsafe_allow_html=True)
        
        # Mode cards
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("""
            <div class="mode-card">
                <div class="mode-icon">💬</div>
                <div class="mode-title">Chat</div>
                <div class="mode-desc">Have a conversation with AI about your study materials</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Chatting", key="chat_btn", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="mode-card">
                <div class="mode-icon">🗂️</div>
                <div class="mode-title">Flashcards</div>
                <div class="mode-desc">Create and review AI-generated flashcards</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create Flashcards", key="flash_btn", use_container_width=True):
                st.session_state.current_page = "flashcards"
                st.rerun()
        
        # Features section
        st.markdown('<div class="feature-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Features</h3>', unsafe_allow_html=True)
        
        feature_col1, feature_col2 = st.columns(2, gap="large")
        
        with feature_col1:
            st.markdown("""
            <div class="feature-card">
                <h4>💬 Smart Chat</h4>
                <ul>
                    <li>Ask questions about your documents</li>
                    <li>Get detailed explanations</li>
                    <li>Context-aware responses</li>
                    <li>Conversational interface</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🗂️ Flashcards</h4>
                <ul>
                    <li>AI-generated from your materials</li>
                    <li>Interactive flip cards</li>
                    <li>Track your progress</li>
                    <li>Mark cards as mastered</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)