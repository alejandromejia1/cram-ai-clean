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

# RAG System Class
class SimpleRAG:
    def __init__(self):
        if 'GROQ_API_KEY' in st.secrets:
            api_key = st.secrets['GROQ_API_KEY']
            
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                # List available models and choose one
                models = self.client.models.list()
                model_list = [model.id for model in models]
                
                # Choose the best available model
                if "llama-3.1-8b-instant" in model_list:
                    self.model_name = "llama-3.1-8b-instant"
                elif "llama3-8b-8192" in model_list:
                    self.model_name = "llama3-8b-8192"
                elif "llama3-70b-8192" in model_list:
                    self.model_name = "llama3-70b-8192"
                else:
                    self.model_name = model_list[0] if model_list else None
                    
                self.current_document = ""
                
            except Exception as e:
                st.error(f"API connection failed: {str(e)}")
                self.client = None
                self.model_name = None
        else:
            st.error("GROQ_API_KEY not found in secrets")
            self.client = None
            self.model_name = None
    
    def add_document(self, text, doc_id):
        if text and text != "Unsupported file type":
            self.current_document = text
    
    def query(self, question):
        if not self.client or not self.model_name:
            return "System not ready - check API key status."
        if not self.current_document:
            return "Please upload a document first."
            
        try:
            with st.spinner("Finding answer..."):
                prompt = f"""Based ONLY on the following context:

{self.current_document}

Question: {question}

Answer based only on the context above:"""
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1
                )
                return f"**Answer:** {response.choices[0].message.content}"
        except Exception as e:
            return f"Error: {str(e)}"

# Main App
st.set_page_config(page_title="Cram AI", layout="centered")

st.title("Cram AI")
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
    1. **Upload** a PDF, PowerPoint, or image of study materials
    2. **Wait** for processing to complete
    3. **Ask questions** about your specific content
    4. **Test different file types** to see what works best

    **Supported formats:**
    - PDF documents
    - PowerPoint (.pptx) presentations
    - Images with text (PNG, JPG)
    """)
