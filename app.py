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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Clean, professional CSS - no emojis, no Streamlit defaults
st.markdown("""
<style>
    /* Reset everything */
    .main {
        padding: 0 !important;
    }
    
    .stApp {
        background: #ffffff;
    }
    
    /* Header */
    .app-header {
        padding: 3rem 0 2rem 0;
        text-align: center;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 3rem;
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        color: #000000;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #666666;
        margin: 0;
        font-weight: 400;
    }
    
    /* Main content */
    .main-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Upload section */
    .upload-section {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
    }
    
    .upload-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #000000;
        margin: 0 0 1rem 0;
    }
    
    .upload-description {
        color: #666666;
        margin: 0 0 2rem 0;
        line-height: 1.5;
    }
    
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 3rem 2rem;
        background: #ffffff;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #000000;
        background: #fafafa;
    }
    
    .upload-area-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #000000;
        margin: 0 0 0.5rem 0;
    }
    
    .upload-area-subtitle {
        color: #666666;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Chat interface */
    .chat-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .message {
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        line-height: 1.6;
        max-width: 80%;
        font-size: 1rem;
    }
    
    .user-message {
        background: #000000;
        color: #ffffff;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #333333;
        border: 1px solid #e9ecef;
        border-bottom-left-radius: 4px;
    }
    
    .welcome-state {
        text-align: center;
        padding: 4rem 2rem;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        color: #000000;
        margin: 0 0 1rem 0;
    }
    
    .welcome-description {
        color: #666666;
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Hide all Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    .stChatInput {
        border: 1px solid #e9ecef !important;
        border-radius: 24px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">Cram</h1>
    <p class="app-subtitle">Upload documents. Ask questions. Get answers.</p>
</div>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Upload section
st.markdown("""
<div class="upload-section">
    <h2 class="upload-title">Add your study materials</h2>
    <p class="upload-description">Upload PDFs, PowerPoint presentations, or images to start asking questions about your content.</p>
    <div class="upload-area">
        <div class="upload-area-title">Drop files here or click to browse</div>
        <div class="upload-area-subtitle">Supports PDF, PPTX, PNG, JPG, JPEG • Max 200MB per file</div>
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
            with st.spinner(f"Processing {uploaded_file.name}..."):
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
            <h2 class="welcome-title">Ready to explore your documents</h2>
            <p class="welcome-description">Ask questions about your uploaded materials and receive answers based on the content.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        response = rag.query(prompt)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Document management
    if rag.documents:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
            selected_doc = st.selectbox(
                "Active document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0
            )
            rag.switch_document(selected_doc)
        
        with col2:
            if st.button("Clear conversation", use_container_width=True):
                rag.clear_conversation()
                st.rerun()
        
        with col3:
            if st.button("Remove document", use_container_width=True):
                rag.delete_document(selected_doc)
                st.rerun()

else:
    st.markdown("""
    <div class="welcome-state">
        <h2 class="welcome-title">Get started with your materials</h2>
        <p class="welcome-description">Upload your study documents above to begin asking questions and exploring the content.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
