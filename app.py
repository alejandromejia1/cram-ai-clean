import streamlit as st
import uuid
from file_processor import FileProcessor
from rag_system import SimpleRAG

# Initialize RAG system
if 'rag' not in st.session_state:
    st.session_state.rag = SimpleRAG()

rag = st.session_state.rag

# Main App
st.set_page_config(page_title="Cram AI", layout="wide")

# Beautiful, clean CSS - no AI branding, professional look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
        letter-spacing: -0.025em;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    .sidebar-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .info-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 0;
        border: 1px solid #e5e7eb;
    }
    
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Cram</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Study materials, organized and understood</div>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([3, 1])

with col1:
    # Chat interface - ALWAYS show when documents exist
    if hasattr(rag, 'documents') and rag.documents:
        conversation_history = rag.get_conversation_history()
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # If no conversation yet, show welcome message
        if not conversation_history:
            st.write("")
            st.write("")
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                st.write("👋 Ready to explore your documents. Ask anything about the content.")
            st.write("")
            st.write("")
        
        # Display conversation history
        for conv in conversation_history:
            # User message - clean bubble
            user_col1, user_col2 = st.columns([1, 6])
            with user_col2:
                st.markdown(f"""
                <div style='
                    background: #3b82f6;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px 18px 4px 18px;
                    margin: 8px 0;
                    font-weight: 500;
                '>
                    {conv['question']}
                </div>
                """, unsafe_allow_html=True)
            
            # Assistant message - clean bubble  
            assistant_col1, assistant_col2 = st.columns([6, 1])
            with assistant_col1:
                st.markdown(f"""
                <div style='
                    background: #f3f4f6;
                    color: #111827;
                    padding: 12px 16px;
                    border-radius: 18px 18px 18px 4px;
                    margin: 8px 0;
                    border: 1px solid #e5e7eb;
                '>
                    {conv['answer']}
                </div>
                """, unsafe_allow_html=True)
        
        # Current input at bottom
        if prompt := st.chat_input("Ask a question about your document..."):
            # Get response
            response = rag.query(prompt)
            # Rerun to show new messages
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # No documents state
        st.markdown("""
        <div style='
            text-align: center; 
            padding: 4rem 2rem; 
            color: #6b7280;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        '>
            <h3 style='color: #111827; margin-bottom: 1rem;'>Get started with your materials</h3>
            <p>Upload documents to begin asking questions and exploring content.</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### Overview")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    if hasattr(rag, 'documents') and rag.documents:
        st.write(f"**Documents**\n{len(rag.documents)}")
        current_conv = rag.get_conversation_history()
        st.write(f"**Messages**\n{len(current_conv)}")
        
        if rag.get_current_document():
            doc_name = rag.documents[rag.current_doc_id]['filename']
            st.write(f"**Active**\n{doc_name}")
    else:
        st.write("No documents yet")
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for file management
with st.sidebar:
    st.markdown("### Materials")
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    
    # File upload
    uploaded_files = st.file_uploader(
        "Add study materials",
        type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="PDF, PowerPoint, Images",
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
                        st.error(f"Couldn't process: {uploaded_file.name}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Document management
    if hasattr(rag, 'documents') and rag.documents:
        st.markdown("### Current Document")
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        
        doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
        if doc_options:
            selected_doc = st.selectbox(
                "Select document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0,
                label_visibility="collapsed"
            )
            rag.switch_document(selected_doc)
            
            # Conversation controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Chat", use_container_width=True, key="clear_chat"):
                    rag.clear_conversation()
                    st.rerun()
            with col2:
                if st.button("Remove Doc", use_container_width=True, key="delete_doc"):
                    rag.delete_document(selected_doc)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Instructions
with st.expander("How to use this workspace"):
    st.markdown("""
    1. **Add materials** in the sidebar
    2. **Select** which document to focus on  
    3. **Ask questions** about the content
    4. **Explore** and understand your materials
    
    All responses are based solely on your uploaded documents.
    """)
