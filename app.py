import streamlit as st
import os
from PyPDF2 import PdfReader
from pptx import Presentation
import pytesseract
from PIL import Image
import io
import uuid
from openai import OpenAI

# File Processor Class
class FileProcessor:
    @staticmethod
    def extract_pdf_text(file):
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def extract_ppt_text(file):
        prs = Presentation(file)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    
    @staticmethod
    def extract_image_text(file):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text
    
    @staticmethod
    def process_file(uploaded_file):
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            return FileProcessor.extract_pdf_text(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return FileProcessor.extract_ppt_text(uploaded_file)
        elif file_type.startswith('image'):
            return FileProcessor.extract_image_text(uploaded_file)
        else:
            return "Unsupported file type"

# RAG System Class - WITH BETTER DEBUGGING
class SimpleRAG:
    def __init__(self):
        st.write("🔍 DEBUG: Checking Streamlit secrets...")
        st.write(f"Available secrets: {list(st.secrets.keys())}")
        
        if 'GROQ_API_KEY' in st.secrets:
            api_key = st.secrets['GROQ_API_KEY']
            st.write(f"📋 Groq Key found: {api_key[:25]}...")
            
            # Check if it's placeholder
            if "your_groq_key" in api_key or "gsk_xxxxxxxx" in api_key:
                st.error("❌ PLACEHOLDER KEY: Please add your real Groq API key")
                self.client = None
                return
                
            try:
                st.write("🔄 Testing Groq connection...")
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                # Test the connection
                models = self.client.models.list()
                st.success(f"✅ GROQ CONNECTED! Available models: {len(list(models))}")
                self.current_document = ""
            except Exception as e:
                st.error(f"❌ Groq connection failed: {str(e)}")
                self.client = None
        else:
            st.error("❌ GROQ_API_KEY not found in secrets")
            st.info("Please add GROQ_API_KEY to Streamlit secrets")
            self.client = None
    
    def add_document(self, text, doc_id):
        if text and text != "Unsupported file type":
            self.current_document = text
            st.success("📄 Document loaded successfully!")
    
    def query(self, question):
        if not self.client:
            return "System not ready - check API key status above."
        if not self.current_document:
            return "Please upload a document first."
            
        try:
            with st.spinner("🤔 Analyzing with Groq..."):
                prompt = f"""Based ONLY on the following context:

{self.current_document}

Question: {question}

Answer based only on the context above:"""
                
                response = self.client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1
                )
                return f"**Answer:** {response.choices[0].message.content}"
        except Exception as e:
            return f"❌ Error during query: {str(e)}"

# Main App
st.set_page_config(page_title="Cram AI", layout="centered")

st.title("Cram AI 🚀")
st.markdown("Upload your study materials and get instant answers")

# Initialize RAG system
if 'rag' not in st.session_state:
    st.session_state.rag = SimpleRAG()

rag = st.session_state.rag

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
            st.session_state['processed'] = True
            
            with st.expander("Preview extracted text"):
                st.text_area("Extracted Content", text[:1000] + "..." if len(text) > 1000 else text, height=200)
        else:
            st.error("Could not extract text from this file. Try a different format.")

if st.session_state.get('processed', False):
    st.divider()
    st.subheader("Ask Questions")
    
    question = st.text_input("What would you like to know about your document?")
    
    if question:
        answer = rag.query(question)
        st.markdown("### Answer:")
        st.write(answer)

with st.expander("How to use Cram AI"):
    st.markdown("""
    1. **Upload** a PDF, PowerPoint, or image
    2. **Wait** for processing  
    3. **Ask questions** about your content
    
    **Supported formats:** PDF, PowerPoint, Images
    """)
