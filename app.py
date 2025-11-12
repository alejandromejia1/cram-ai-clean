import streamlit as st
import uuid
from file_processor import FileProcessor
from rag_system import SimpleRAG

# Initialize RAG system
if 'rag' not in st.session_state:
    st.session_state.rag = SimpleRAG()

# Initialize theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

rag = st.session_state.rag

# Main App
st.set_page_config(
    page_title="Cram AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dynamic CSS for dark/light mode
if st.session_state.dark_mode:
    theme_css = """
    <style>
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            max-width: 700px !important;
        }
        
        /* Dark theme */
        .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }
        
        h1 {
            color: #ffffff !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Header centering */
        .header-container {
            text-align: center !important;
        }
        
        .subtitle {
            color: #cccccc !important;
            text-align: center !important;
            margin-bottom: 2rem !important;
        }
        
        /* Upload area - dark */
        .upload-section {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #333333;
        }
        
        .upload-area {
            border: 2px dashed #444444;
            border-radius: 8px;
            padding: 1.5rem;
            background: #000000;
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .upload-area:hover {
            border-color: #666666;
        }
        
        .upload-title {
            font-size: 1rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0 0 0.25rem 0;
        }
        
        .upload-subtitle {
            color: #999999;
            font-size: 0.85rem;
            margin: 0;
        }
        
        /* Chat styling - dark */
        .message {
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            line-height: 1.5;
            max-width: 80%;
            font-size: 0.95rem;
        }
        
        .user-message {
            background: #333333;
            color: #ffffff;
            margin-left: auto;
            border-bottom-right-radius: 2px;
        }
        
        .assistant-message {
            background: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-bottom-left-radius: 2px;
        }
        
        .welcome-text {
            text-align: center;
            padding: 1.5rem;
            color: #999999;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: absolute;
            top: 1rem;
            right: 1rem;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            max-width: 700px !important;
        }
        
        /* Light theme */
        .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        h1 {
            color: #000000 !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Header centering */
        .header-container {
            text-align: center !important;
        }
        
        .subtitle {
            color: #666666 !important;
            text-align: center !important;
            margin-bottom: 2rem !important;
        }
        
        /* Upload area - light */
        .upload-section {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e9ecef;
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
        
        .upload-title {
            font-size: 1rem;
            font-weight: 600;
            color: #000000;
            margin: 0 0 0.25rem 0;
        }
        
        .upload-subtitle {
            color: #666666;
            font-size: 0.85rem;
            margin: 0;
        }
        
        /* Chat styling - light */
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
        
        .welcome-text {
            text-align: center;
            padding: 1.5rem;
            color: #666666;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: absolute;
            top: 1rem;
            right: 1rem;
        }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# Hide Streamlit elements
st.markdown("""
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    header {visibility: hidden !important;}
    
    .stChatInput > div > div {
        border: 1px solid #333333 !important;
        border-radius: 20px !important;
        padding: 0.75rem 1rem !important;
        background: #1a1a1a !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Theme toggle button
col1, col2, col3 = st.columns([1, 2, 1])
with col3:
    if st.button("Light Mode" if st.session_state.dark_mode else "Dark Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Header with centered alignment
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown("# Cram AI")
st.markdown('<div class="subtitle">Upload documents and ask questions</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Upload section
with st.container():
    st.markdown("### Add study materials")
    st.markdown("PDF, PowerPoint, or images")
    
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
    
    if conversation_history:
        for conv in conversation_history:
            st.markdown(f'<div class="message user-message">{conv["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="message assistant-message">{conv["answer"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="welcome-text">Your documents are ready. Ask a question to get started.</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        response = rag.query(prompt)
        st.rerun()
    
    # Document management
    if rag.documents:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
            selected_doc = st.selectbox(
                "Active document:",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0
            )
            rag.switch_document(selected_doc)
        
        with col2:
            if st.button("Clear chat", use_container_width=True):
                rag.clear_conversation()
                st.rerun()
        
        with col3:
            if st.button("Remove", use_container_width=True):
                rag.delete_document(selected_doc)
                st.rerun()

else:
    st.markdown('<div class="welcome-text">Upload documents to begin</div>', unsafe_allow_html=True)
