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
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
            max-width: 900px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
        
        /* Dark theme */
        .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }
        
        h1 {
            color: #ffffff !important;
            font-size: 3rem !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
            margin-top: 2rem !important;
        }
        
        /* Header centering */
        .header-container {
            text-align: center !important;
            margin-bottom: 3rem !important;
        }
        
        .subtitle {
            color: #cccccc !important;
            text-align: center !important;
            font-size: 1.3rem !important;
            margin-bottom: 3rem !important;
        }
        
        /* Upload area - dark */
        .upload-section {
            background: #1a1a1a;
            border-radius: 16px;
            padding: 2.5rem;
            margin: 2rem 0;
            border: 1px solid #333333;
        }
        
        .upload-area {
            border: 2px dashed #444444;
            border-radius: 12px;
            padding: 2.5rem;
            background: #000000;
            text-align: center;
            transition: all 0.2s ease;
            margin: 1.5rem 0;
        }
        
        .upload-area:hover {
            border-color: #666666;
        }
        
        .upload-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0 0 0.5rem 0;
        }
        
        .upload-subtitle {
            color: #999999;
            font-size: 1rem;
            margin: 0;
        }
        
        /* Theme toggle - positioned in corner */
        .theme-toggle-container {
            position: fixed;
            top: 1.5rem;
            right: 2rem;
            z-index: 9999;
        }
        
        .theme-toggle {
            background: #333333;
            color: white;
            border: 1px solid #555555;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            cursor: pointer;
        }
        
        .theme-toggle:hover {
            background: #444444;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        .main .block-container {
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
            max-width: 900px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }
        
        /* Light theme */
        .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        h1 {
            color: #000000 !important;
            font-size: 3rem !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
            margin-top: 2rem !important;
        }
        
        /* Header centering */
        .header-container {
            text-align: center !important;
            margin-bottom: 3rem !important;
        }
        
        .subtitle {
            color: #666666 !important;
            text-align: center !important;
            font-size: 1.3rem !important;
            margin-bottom: 3rem !important;
        }
        
        /* Upload area - light */
        .upload-section {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 2.5rem;
            margin: 2rem 0;
            border: 1px solid #e9ecef;
        }
        
        .upload-area {
            border: 2px dashed #d1d5db;
            border-radius: 12px;
            padding: 2.5rem;
            background: #ffffff;
            text-align: center;
            transition: all 0.2s ease;
            margin: 1.5rem 0;
        }
        
        .upload-area:hover {
            border-color: #000000;
        }
        
        .upload-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #000000;
            margin: 0 0 0.5rem 0;
        }
        
        .upload-subtitle {
            color: #666666;
            font-size: 1rem;
            margin: 0;
        }
        
        /* Theme toggle - positioned in corner */
        .theme-toggle-container {
            position: fixed;
            top: 1.5rem;
            right: 2rem;
            z-index: 9999;
        }
        
        .theme-toggle {
            background: #f8f9fa;
            color: #000000;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            cursor: pointer;
        }
        
        .theme-toggle:hover {
            background: #e9ecef;
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

# Theme toggle button - positioned in top right corner
st.markdown("""
<div class="theme-toggle-container">
    <button class="theme-toggle" onclick="window.parent.document.querySelector('.theme-toggle-button').click()">
        """ + ("Light Mode" if st.session_state.dark_mode else "Dark Mode") + """
    </button>
</div>
""", unsafe_allow_html=True)

# Create a hidden button for theme toggle
if st.button("Toggle Theme", key="theme_toggle_hidden", help="Toggle between dark and light mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# Add JavaScript to connect the custom button to the hidden Streamlit button
st.markdown("""
<script>
    // Connect custom theme toggle to Streamlit button
    document.addEventListener('click', function(e) {
        if (e.target.closest('.theme-toggle')) {
            window.parent.document.querySelector('[data-testid="baseButton-secondary"]').click();
        }
    });
</script>
""", unsafe_allow_html=True)

# Header with centered alignment and better spacing
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown("# Cram AI")
st.markdown('<div class="subtitle">Upload documents and ask questions</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Upload section with better spacing
with st.container():
    st.markdown("## Add study materials")
    st.markdown("**PDF, PowerPoint, or images**")
    
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
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #666666; font-size: 1.1rem;">
            Your documents are ready. Ask a question to get started.
        </div>
        """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #666666; font-size: 1.1rem;">
        Upload documents to begin
    </div>
    """, unsafe_allow_html=True)
