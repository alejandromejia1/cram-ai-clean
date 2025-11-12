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

# Modern CSS with custom font and no emojis
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
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
    
    /* Remove emojis from chat messages */
    .stChatMessage {
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Cram AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your study materials and chat with them</div>', unsafe_allow_html=True)

# Sidebar for file management
with st.sidebar:
    st.header("Documents")
    
    # File upload in sidebar
    uploaded_files = st.file_uploader(
        "Upload study materials",
        type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Supported: PDF, PowerPoint, Images"
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
        st.subheader("Your Documents")
        
        doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
        if doc_options:
            selected_doc = st.selectbox(
                "Active document:",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=0
            )
            rag.switch_document(selected_doc)
            
            # Conversation controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Chat", use_container_width=True, key="clear_chat"):
                    rag.clear_conversation()
                    st.rerun()
            with col2:
                if st.button("Delete Doc", use_container_width=True, key="delete_doc"):
                    rag.delete_document(selected_doc)
                    st.rerun()

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    # Always show chat interface, even if system isn't fully ready
    if hasattr(rag, 'documents') and rag.documents:
        conversation_history = rag.get_conversation_history()
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # If no conversation yet, show welcome message
            if not conversation_history:
                with st.chat_message("assistant"):
                    if rag.is_ready():
                        st.write("Hi! I'm ready to answer questions about your document. Ask me anything!")
                    else:
                        st.write("Hi! I can see your documents. Ask me anything about them!")
            
            # Display conversation history
            for conv in conversation_history:
                # User message
                with st.chat_message("user"):
                    st.write(conv['question'])
                
                # Assistant message  
                with st.chat_message("assistant"):
                    st.write(conv['answer'])
            
            # Current input at bottom - always show if we have documents
            if prompt := st.chat_input("Ask a question about your document..."):
                # Add user message to chat
                with st.chat_message("user"):
                    st.write(prompt)
                
                # Get and display assistant response
                with st.chat_message("assistant"):
                    response = rag.query(prompt)
                    st.write(response)
                
                # Rerun to update the chat
                st.rerun()
    
    elif not rag.documents:
        st.info("Upload some documents in the sidebar to get started!")

with col2:
    st.header("Info")
    if hasattr(rag, 'documents') and rag.documents:
        st.write(f"**Documents:** {len(rag.documents)}")
        current_conv = rag.get_conversation_history()
        st.write(f"**Messages:** {len(current_conv)}")
        
        if rag.get_current_document():
            doc_name = rag.documents[rag.current_doc_id]['filename']
            st.write(f"**Active:** {doc_name}")
        
        # Removed the API configuration warning
    else:
        st.write("No documents yet")

# Instructions
with st.expander("How to use Cram AI"):
    st.markdown("""
    1. **Upload** documents in the sidebar (PDF, PowerPoint, Images)
    2. **Select** which document to chat with
    3. **Ask questions** in the chat interface
    4. **Continue conversations** naturally
    
    The AI will only answer based on your uploaded documents.
    """)
