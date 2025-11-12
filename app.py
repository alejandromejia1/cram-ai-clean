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
    page_title="Cram | Study Smarter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS inspired by modern SaaS platforms
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .app-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .logo {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .tagline {
        color: #6b7280;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Content area */
    .content-area {
        background: white;
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Upload area styling */
    .upload-container {
        border: 2px dashed #e5e7eb;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: #fafafa;
        transition: all 0.3s ease;
        margin: 2rem 0;
    }
    
    .upload-container:hover {
        border-color: #667eea;
        background: #f0f4ff;
        transform: translateY(-2px);
    }
    
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #667eea;
    }
    
    .upload-text {
        font-size: 1.2rem;
        color: #374151;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .upload-subtext {
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    /* Chat interface */
    .chat-container {
        background: #f8fafc;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 20px 20px 6px 20px;
        margin: 1rem 0 1rem auto;
        max-width: 70%;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        font-weight: 500;
    }
    
    .message-assistant {
        background: white;
        color: #374151;
        padding: 1.2rem 1.5rem;
        border-radius: 20px 20px 20px 6px;
        margin: 1rem auto 1rem 0;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        line-height: 1.6;
    }
    
    /* Welcome state */
    .welcome-state {
        text-align: center;
        padding: 4rem 2rem;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        color: #667eea;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        line-height: 1.6;
        max-width: 500px;
        margin: 0 auto 2rem auto;
    }
    
    /* Stats panel */
    .stats-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="app-header">
    <div class="header-content">
        <h1 class="logo">cram</h1>
        <p class="tagline">AI-powered study assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content Area
st.markdown('<div class="content-area">', unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns([2, 1])

with col1:
    # Chat Interface
    if hasattr(rag, 'documents') and rag.documents:
        conversation_history = rag.get_conversation_history()
        
        if conversation_history:
            st.markdown("### Conversation")
            for conv in conversation_history:
                st.markdown(f'<div class="message-user">{conv["question"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="message-assistant">{conv["answer"]}</div>', unsafe_allow_html=True)
        else:
            # Welcome state with documents
            st.markdown("""
            <div class="welcome-state">
                <div class="welcome-icon">📚</div>
                <h2 class="welcome-title">Ready to learn</h2>
                <p class="welcome-subtitle">Your documents are processed and ready. Ask anything about the content to get started.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your document..."):
            response = rag.query(prompt)
            st.rerun()
            
    else:
        # Empty state
        st.markdown("""
        <div class="welcome-state">
            <div class="welcome-icon">🎯</div>
            <h2 class="welcome-title">Start studying smarter</h2>
            <p class="welcome-subtitle">Upload your study materials and get instant answers to your questions using AI-powered analysis.</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # Upload Section
    st.markdown("### Add Materials")
    st.markdown("""
    <div class="upload-container">
        <div class="upload-icon">📁</div>
        <div class="upload-text">Drag & drop files</div>
        <div class="upload-subtext">PDF, PowerPoint, or images</div>
    </div>
    """, unsafe_allow_html=True)
    
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
                        st.success(f"✓ {uploaded_file.name}")
                    else:
                        st.error(f"Couldn't process {uploaded_file.name}")
    
    # Stats Panel
    if hasattr(rag, 'documents') and rag.documents:
        st.markdown("### Overview")
        st.markdown('<div class="stats-panel">', unsafe_allow_html=True)
        
        current_conv = rag.get_conversation_history()
        st.markdown(f'<div class="stat-number">{len(rag.documents)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Documents</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="stat-number">{len(current_conv)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Messages</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Document management
        if rag.documents:
            st.markdown("### Active Document")
            doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
            selected_doc = st.selectbox(
                "Choose document",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0,
                label_visibility="collapsed"
            )
            rag.switch_document(selected_doc)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    rag.clear_conversation()
                    st.rerun()
            with col2:
                if st.button("🗑️ Remove Doc", use_container_width=True):
                    rag.delete_document(selected_doc)
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Hide Streamlit elements
st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 60%; background: white; border-radius: 50px; padding: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;}
</style>
""", unsafe_allow_html=True)
