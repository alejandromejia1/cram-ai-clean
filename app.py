import streamlit as st
import uuid
from file_processor import FileProcessor
from rag_system import SimpleRAG

# Initialize RAG system
if 'rag' not in st.session_state:
    st.session_state.rag = SimpleRAG()

rag = st.session_state.rag

# Main App
st.set_page_config(
    page_title="Cram",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - Clean, modern, no Streamlit defaults
st.markdown("""
<style>
    /* Reset and base styles */
    .main {
        padding: 0 !important;
    }
    
    .stApp {
        background: #ffffff;
    }
    
    /* Header */
    .header {
        padding: 2rem 0 1rem 0;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    
    .logo {
        font-size: 2.5rem;
        font-weight: 700;
        color: #000;
        margin: 0;
    }
    
    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Main content grid */
    .content-grid {
        display: grid;
        grid-template-columns: 1fr 400px;
        gap: 3rem;
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Chat area */
    .chat-area {
        min-height: 600px;
    }
    
    .message {
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        line-height: 1.5;
        max-width: 80%;
    }
    
    .user-message {
        background: #000;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333;
        border: 1px solid #e9ecef;
        border-bottom-left-radius: 4px;
    }
    
    /* Upload area */
    .upload-section {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .upload-placeholder {
        border: 2px dashed #dee2e6;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        background: white;
        transition: all 0.2s;
    }
    
    .upload-placeholder:hover {
        border-color: #000;
    }
    
    .upload-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        opacity: 0.7;
    }
    
    .upload-text {
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #333;
    }
    
    .upload-subtext {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Stats */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #000;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Welcome state */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #000;
    }
    
    .welcome-subtitle {
        color: #666;
        font-size: 1.1rem;
        line-height: 1.6;
        max-width: 500px;
        margin: 0 auto;
    }
    
    /* Hide all Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    .stChatInput {border: 1px solid #e9ecef !important; border-radius: 24px !important; padding: 1rem !important;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <div style="max-width: 1400px; margin: 0 auto; padding: 0 2rem;">
        <h1 class="logo">cram</h1>
        <p class="subtitle">Upload documents. Ask questions. Get answers.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content
st.markdown("""
<div class="content-grid">
    <div class="chat-area">
""", unsafe_allow_html=True)

# Chat interface
if hasattr(rag, 'documents') and rag.documents:
    conversation_history = rag.get_conversation_history()
    
    if conversation_history:
        for conv in conversation_history:
            st.markdown(f'<div class="message user-message">{conv["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="message assistant-message">{conv["answer"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-icon">📚</div>
            <h2 class="welcome-title">Documents ready</h2>
            <p class="welcome-subtitle">Ask anything about your uploaded materials and get instant answers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        response = rag.query(prompt)
        st.rerun()
else:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">✨</div>
        <h2 class="welcome-title">Study smarter</h2>
        <p class="welcome-subtitle">Upload your PDFs, slides, or images to start asking questions and understanding your materials faster.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    </div>
    <div class="upload-section">
        <h3 style="margin: 0 0 1.5rem 0; color: #333;">Add materials</h3>
        <div class="upload-placeholder">
            <div class="upload-icon">📄</div>
            <div class="upload-text">Drop files here</div>
            <div class="upload-subtext">PDF, PowerPoint, Images</div>
        </div>
""", unsafe_allow_html=True)

# File uploader
uploaded_files = st.file_uploader(
    "Upload files",
    type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# Process files
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_exists = hasattr(rag, 'documents') and any(doc['filename'] == uploaded_file.name for doc in rag.documents.values())
        
        if not file_exists:
            with st.spinner(f"Adding {uploaded_file.name}..."):
                text = FileProcessor.process_file(uploaded_file)
                
                if text != "Unsupported file type" and len(text.strip()) > 0:
                    doc_id = str(uuid.uuid4())
                    rag.add_document(text, doc_id, uploaded_file.name)
                    st.success(f"Added: {uploaded_file.name}")
                else:
                    st.error(f"Failed: {uploaded_file.name}")

# Stats and document management
if hasattr(rag, 'documents') and rag.documents:
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Documents</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Messages</div>
        </div>
    </div>
    """.format(len(rag.documents), len(rag.get_conversation_history())), unsafe_allow_html=True)
    
    # Document selector
    doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
    selected_doc = st.selectbox(
        "Active document",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x],
        index=0
    )
    rag.switch_document(selected_doc)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear chat", use_container_width=True):
            rag.clear_conversation()
            st.rerun()
    with col2:
        if st.button("Remove document", use_container_width=True):
            rag.delete_document(selected_doc)
            st.rerun()

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)
