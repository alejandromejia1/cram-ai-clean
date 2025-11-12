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
    layout="wide",
    page_icon="📚"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    .document-item {
        padding: 0.5rem;
        border-radius: 0.375rem;
        margin: 0.25rem 0;
    }
    .info-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Cram AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your study materials and chat with them</div>', unsafe_allow_html=True)

# Sidebar for file management
with st.sidebar:
    st.markdown('<div class="sidebar-header">Documents</div>', unsafe_allow_html=True)
    
    # File upload in sidebar
    uploaded_files = st.file_uploader(
        "Upload study materials",
        type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Supported: PDF, PowerPoint, Images",
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
                        st.success(f"Processed: {uploaded_file.name}")
                    else:
                        st.error(f"Failed: {uploaded_file.name}")
    
    # Document management
    if hasattr(rag, 'documents') and rag.documents:
        st.divider()
        st.markdown('<div class="sidebar-header">Your Documents</div>', unsafe_allow_html=True)
        
        doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
        if doc_options:
            selected_doc = st.selectbox(
                "Active document:",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0,
                label_visibility="collapsed"
            )
            rag.switch_document(selected_doc)
            
            # Conversation controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Chat", use_container_width=True, type="secondary"):
                    rag.clear_conversation()
                    st.rerun()
            with col2:
                if st.button("Delete Document", use_container_width=True, type="secondary"):
                    rag.delete_document(selected_doc)
                    st.rerun()

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    # Display conversation in chat style
    if rag.is_ready() and rag.get_current_document():
        conversation_history = rag.get_conversation_history()
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # If no conversation yet, show welcome message
            if not conversation_history:
                with st.chat_message("assistant"):
                    st.write("Hi! I'm ready to answer questions about your document. Ask me anything!")
            
            # Display conversation history
            for conv in conversation_history:
                # User message
                with st.chat_message("user"):
                    st.write(conv['question'])
                
                # Assistant message  
                with st.chat_message("assistant"):
                    st.write(conv['answer'])
            
            # Current input at bottom
            if prompt := st.chat_input("Ask a question about your document..."):
                # Add user message to chat
                with st.chat_message("user"):
                    st.write(prompt)
                
                # Get and display assistant response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = rag.query(prompt)
                        st.write(response)
                
                # Rerun to update the chat
                st.rerun()
    
    elif rag.is_ready() and not hasattr(rag, 'documents'):
        st.info("Upload some documents in the sidebar to get started!")
    
    elif not rag.is_ready():
        st.warning("System initializing...")

with col2:
    st.markdown("### Info")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    if hasattr(rag, 'documents') and rag.documents:
        st.write(f"**Documents:** {len(rag.documents)}")
        current_conv = rag.get_conversation_history()
        st.write(f"**Messages:** {len(current_conv)}")
        
        if rag.get_current_document():
            doc_name = rag.documents[rag.current_doc_id]['filename']
            st.write(f"**Active:** {doc_name}")
    else:
        st.write("No documents yet")
    st.markdown('</div>', unsafe_allow_html=True)

# Instructions
with st.expander("How to use Cram AI"):
    st.markdown("""
    1. **Upload** documents in the sidebar (PDF, PowerPoint, Images)
    2. **Select** which document to chat with
    3. **Ask questions** in the chat interface
    4. **Continue conversations** naturally
    
    The AI will only answer based on your uploaded documents.
    """)
