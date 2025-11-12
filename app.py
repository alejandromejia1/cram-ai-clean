import streamlit as st
import os
from file_processor import FileProcessor
from rag_system import SimpleRAG
import uuid

st.set_page_config(
    page_title="Cram AI",
    page_icon="❓",
    layout="centered"
)

@st.cache_resource
def get_rag_system():
    return SimpleRAG()

rag = get_rag_system()

st.title("Cram AI")
st.markdown("Upload your study materials and get instant answers")

uploaded_file = st.file_uploader(
    "Upload study materials",
    type=['pdf', 'pptx', 'png', 'jpg', 'jpeg'],
    help="Supported: PDF, PowerPoint, Images"
)

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    
    with st.spinner("Processing your file..."):
        text = FileProcessor.process_file(uploaded_file)
        
        if text != "Unsupported file type" and len(text.strip()) > 0:
            doc_id = str(uuid.uuid4())
            rag.add_document(text, doc_id)
            st.session_state['current_doc'] = doc_id
            st.session_state['processed'] = True
            
            st.success("File processed successfully!")
            
            with st.expander("Preview extracted text"):
                st.text_area("Extracted Content", text[:1000] + "..." if len(text) > 1000 else text, height=200)
        else:
            st.error("Could not extract text from this file. Try a different format.")

if st.session_state.get('processed', False):
    st.divider()
    st.subheader("Ask Questions")
    
    question = st.text_input("What would you like to know about your document?")
    
    if question:
        with st.spinner("Finding answer..."):
            answer = rag.query(question)
            st.markdown("### Answer:")
            st.write(answer)

with st.expander("How to use Cram AI"):
    st.markdown("""
    1. **Upload** a PDF, PowerPoint, or image of study materials
    2. **Wait** for processing to complete
    3. **Ask questions** about your specific content
    4. **Test different file types** to see what works best

    **Supported formats:**
    - PDF documents
    - PowerPoint (.pptx) presentations
    - Images with text (PNG, JPG)

    *Cram AI reads your actual files - no more converting between formats!*
    """)
