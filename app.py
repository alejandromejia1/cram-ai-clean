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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dynamic CSS for dark/light mode
if st.session_state.dark_mode:
    theme_css = """
    <style>
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 800px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
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
            margin-bottom: 0.25rem !important;
        }
        
        .subtitle {
            color: #cccccc !important;
            text-align: center !important;
            margin-bottom: 2rem !important;
        }
        
        /* Upload area - dark */
        .section {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #333333;
        }
        
        /* Chat messages */
        .user-msg {
            background: #333333;
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 18px 18px 4px 18px;
            margin: 0.5rem 0 0.5rem auto;
            max-width: 70%;
            word-wrap: break-word;
        }
        
        .assistant-msg {
            background: #2a2a2a;
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 18px 18px 18px 4px;
            margin: 0.5rem auto 0.5rem 0;
            max-width: 70%;
            border: 1px solid #333333;
            word-wrap: break-word;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: #333333;
            color: white;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            cursor: pointer;
            z-index: 1000;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 800px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
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
            margin-bottom: 0.25rem !important;
        }
        
        .subtitle {
            color: #666666 !important;
            text-align: center !important;
            margin-bottom: 2rem !important;
        }
        
        /* Upload area - light */
        .section {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e9ecef;
        }
        
        /* Chat messages */
        .user-msg {
            background: #000000;
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 18px 18px 4px 18px;
            margin: 0.5rem 0 0.5rem auto;
            max-width: 70%;
            word-wrap: break-word;
        }
        
        .assistant-msg {
            background: #f8f9fa;
            color: #333333;
            padding: 0.75rem 1rem;
            border-radius: 18px 18px 18px 4px;
            margin: 0.5rem auto 0.5rem 0;
            max-width: 70%;
            border: 1px solid #e9ecef;
            word-wrap: break-word;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: #f8f9fa;
            color: #000000;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            cursor: pointer;
            z-index: 1000;
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
</style>
""", unsafe_allow_html=True)

# Theme toggle
st.markdown(f"""
<div class="theme-toggle" onclick="this.style.display='none'">
    <div style="display: none">
        {st.button("Toggle Theme", key="theme_toggle")}
    </div>
    {'Light Mode' if st.session_state.dark_mode else 'Dark Mode'}
</div>
""", unsafe_allow_html=True)

if st.session_state.get('theme_toggle'):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# Header
st.markdown("# Cram AI")
st.markdown('<div class="subtitle">Upload documents and ask questions</div>', unsafe_allow_html=True)

# Upload section
with st.container():
    st.markdown("## Add study materials")
    st.markdown("**PDF, PowerPoint, or images**")
    
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
    
    # Display conversation
    for conv in conversation_history:
        st.markdown(f'<div class="user-msg">{conv["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-msg">{conv["answer"]}</div>', unsafe_allow_html=True)
    
    # Welcome message if no conversation
    if not conversation_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            Your documents are ready. Ask a question to get started.
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input - FIXED: This should work now
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Display user message immediately
        st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)
        
        # Get and display assistant response
        response = rag.query(prompt)
        st.markdown(f'<div class="assistant-msg">{response}</div>', unsafe_allow_html=True)
        
        # Rerun to update the state
        st.rerun()
    
    # Document management
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
        if st.button("Remove document", use_container_width=True):
            rag.delete_document(selected_doc)
            st.rerun()

else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #666;">
        Upload documents to begin
    </div>
    """, unsafe_allow_html=True)
