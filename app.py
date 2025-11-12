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

# Simple, clean CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
        max-width: 700px !important;
    }
    
    h1 {
        color: #000000 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    header {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# Simple header
st.markdown("# Cram AI")
st.markdown("Upload documents and ask questions")
st.markdown("---")

# Upload section
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
            st.markdown(f"**You:** {conv['question']}")
            st.markdown(f"**AI:** {conv['answer']}")
            st.markdown("---")
    else:
        st.info("Your documents are ready. Ask a question to get started.")
    
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
    st.info("Upload documents to begin")
