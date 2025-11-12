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
    page_title="Cram AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Compact, professional CSS
st.markdown("""
<style>
    .main {
        padding: 0 !important;
    }
    
    .stApp {
        background: #ffffff;
    }
    
    /* Header */
    .app-header {
        padding: 2rem 0 1rem 0;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #000000;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        color: #666666;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Main content */
    .main-content {
        max-width: 700px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }
    
    /* Upload section */
    .upload-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 1.5rem;
        background: #ffffff;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .upload-area:hover {
        border-color: #000000;
    }
    
    .upload-area-title {
        font-size: 1rem;
        font-weight: 600;
        color: #000000;
        margin: 0 0 0.25rem 0;
    }
    
    .upload-area-subtitle {
        color: #666666;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* Chat interface */
    .chat-container {
        margin: 1rem 0;
    }
    
    .message {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        line-height: 1.5;
        max-width: 80%;
        font-size: 0.95rem;
    }
    
    .user-message {
        background: #000000;
        color: #ffffff;
        margin-left: auto;
        border-bottom-right-radius: 2px;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333333;
        border: 1px solid #e9ecef;
        border-bottom-left-radius: 2px;
    }
    
    .welcome-state {
        text-align: center;
        padding: 1.5rem;
        color: #666666;
    }
    
    /* Controls */
    .controls {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
        align-items: center;
    }
    
    /* Hide all Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    .stChatInput {
        border: 1px solid #e9ecef !important;
        border-radius: 20px !important;
        padding: 0.75rem 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">Cram AI</h1>
    <p class="app-subtitle">Upload documents and ask questions</p>
</div>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Upload section
st.markdown("""
<div class="upload-section">
    <div class="upload-area">
        <div class="upload-area-title">Add study materials</div>
        <div class="upload-area-subtitle">PDF, PowerPoint, or images</div>
    </div>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_files = st.file_uploader(
    "Upload files",
    type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# Process uploaded files
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
                    st.error(f"Could not process: {uploaded_file.name}")

# Chat interface
if hasattr(rag, 'documents') and rag.documents:
    conversation_history = rag.get_conversation_history()
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if conversation_history:
        for conv in conversation_history:
            st.markdown(f'<div class="message user-message">{conv["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="message assistant-message">{conv["answer"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-state">
            Your documents are ready. Ask a question to get started.
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        response = rag.query(prompt)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Document management
    if rag.documents:
        st.markdown('<div class="controls">', unsafe_allow_html=True)
        
        doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
        selected_doc = st.selectbox(
            "Document:",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
            index=0,
            label_visibility="collapsed"
        )
        rag.switch_document(selected_doc)
        
        if st.button("Clear chat", use_container_width=True):
            rag.clear_conversation()
            st.rerun()
        
        if st.button("Remove", use_container_width=True):
            rag.delete_document(selected_doc)
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="welcome-state">
        Upload documents to begin
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
