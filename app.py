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
    page_title="Cram - Study Smarter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional, consumer-ready CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #6b7280;
        margin-bottom: 3rem;
        font-weight: 400;
        line-height: 1.5;
    }
    
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 1rem;
    }
    
    .upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 2.5rem 1rem;
        text-align: center;
        background: #fafafa;
        margin: 1rem 0;
        transition: all 0.2s;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: #f0f7ff;
    }
    
    .document-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .chat-message-user {
        background: #3b82f6;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 6px 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    
    .chat-message-assistant {
        background: #f8fafc;
        color: #111827;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 6px;
        margin: 0.5rem 0;
        max-width: 80%;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .info-panel {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    .stButton button {
        border-radius: 10px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border: 1px solid #d1d5db;
    }
    
    .stButton button:hover {
        border-color: #3b82f6;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    st.markdown('<div class="main-header">Cram</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload your study materials and get instant answers to your questions</div>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Chat Interface
    if hasattr(rag, 'documents') and rag.documents:
        conversation_history = rag.get_conversation_history()
        
        # Display conversation history
        for conv in conversation_history:
            # User message
            st.markdown(f'<div class="chat-message-user">{conv["question"]}</div>', unsafe_allow_html=True)
            # Assistant message
            st.markdown(f'<div class="chat-message-assistant">{conv["answer"]}</div>', unsafe_allow_html=True)
        
        # Welcome message if no conversation
        if not conversation_history:
            st.markdown("""
            <div class="welcome-card">
                <h3 style='margin: 0 0 1rem 0; font-size: 1.5rem;'>Ready to explore your documents</h3>
                <p style='margin: 0; opacity: 0.9;'>Ask questions about the content and get instant answers.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your document..."):
            response = rag.query(prompt)
            st.rerun()
            
    else:
        # Empty state
        st.markdown("""
        <div style='
            text-align: center; 
            padding: 4rem 2rem; 
            color: #6b7280;
            background: #f8fafc;
            border-radius: 20px;
            border: 2px dashed #d1d5db;
            margin: 2rem 0;
        '>
            <h3 style='color: #111827; margin-bottom: 1rem;'>No documents yet</h3>
            <p>Upload your study materials to get started</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # Info Panel
    st.markdown('<div class="info-panel">', unsafe_allow_html=True)
    st.markdown('### Overview')
    st.markdown('---')
    
    if hasattr(rag, 'documents') and rag.documents:
        st.write(f"**Documents**  \n{len(rag.documents)}")
        current_conv = rag.get_conversation_history()
        st.write(f"**Messages**  \n{len(current_conv)}")
        
        if rag.get_current_document():
            doc_name = rag.documents[rag.current_doc_id]['filename']
            st.write(f"**Active Document**  \n{doc_name}")
    else:
        st.write("No documents uploaded")
        
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">Upload Documents</div>', unsafe_allow_html=True)
    
    # File upload with better styling
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Supported formats: PDF, PowerPoint, Images",
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
                        st.success(f"✓ {uploaded_file.name}")
                    else:
                        st.error(f"✗ {uploaded_file.name}")
    
    # Document management
    if hasattr(rag, 'documents') and rag.documents:
        st.markdown("---")
        st.markdown('<div class="sidebar-header">Document Management</div>', unsafe_allow_html=True)
        
        doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
        if doc_options:
            selected_doc = st.selectbox(
                "Select active document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0,
                label_visibility="collapsed"
            )
            rag.switch_document(selected_doc)
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Chat", use_container_width=True, type="secondary"):
                    rag.clear_conversation()
                    st.rerun()
            with col2:
                if st.button("Remove", use_container_width=True, type="secondary"):
                    rag.delete_document(selected_doc)
                    st.rerun()

# Footer instructions
with st.expander("How to use Cram"):
    st.markdown("""
    **1. Upload** - Add your PDFs, PowerPoint files, or images  
    **2. Select** - Choose which document to ask questions about  
    **3. Ask** - Get instant answers based on your materials  
    **4. Learn** - Understand your content faster and more effectively
    
    All responses are generated from your uploaded documents only.
    """)

# Hide Streamlit branding
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)
