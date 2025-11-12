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
        self.documents = {}
        self.current_doc_id = None
        self.client = None
        self.model_name = None
        self.conversations = {}
        
        if 'GROQ_API_KEY' in st.secrets:
            api_key = st.secrets['GROQ_API_KEY']
            
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                models = self.client.models.list()
                model_list = [model.id for model in models]
                
                if "llama-3.1-8b-instant" in model_list:
                    self.model_name = "llama-3.1-8b-instant"
                else:
                    self.model_name = model_list[0] if model_list else None
                    
                st.success("✅ System ready!")
                
            except Exception as e:
                st.error(f"API connection failed: {str(e)}")
                self.client = None
                self.model_name = None
        else:
            st.error("GROQ_API_KEY not found in secrets")
            self.client = None
            self.model_name = None
    
    def is_ready(self):
        return self.client is not None and self.model_name is not None
    
    def add_document(self, text, doc_id, filename):
        if text and text != "Unsupported file type":
            self.documents[doc_id] = {
                'text': text,
                'filename': filename,
                'processed': True
            }
            if doc_id not in self.conversations:
                self.conversations[doc_id] = []
            
            if self.current_doc_id is None:
                self.current_doc_id = doc_id
    
    def switch_document(self, doc_id):
        if doc_id in self.documents:
            self.current_doc_id = doc_id
    
    def delete_document(self, doc_id):
        if doc_id in self.documents:
            del self.documents[doc_id]
            if doc_id in self.conversations:
                del self.conversations[doc_id]
            if self.current_doc_id == doc_id:
                self.current_doc_id = list(self.documents.keys())[0] if self.documents else None
    
    def get_current_document(self):
        if self.current_doc_id and self.current_doc_id in self.documents:
            return self.documents[self.current_doc_id]['text']
        return None
    
    def get_conversation_history(self):
        if self.current_doc_id and self.current_doc_id in self.conversations:
            return self.conversations[self.current_doc_id]
        return []
    
    def add_to_conversation(self, question, answer):
        if self.current_doc_id:
            if self.current_doc_id not in self.conversations:
                self.conversations[self.current_doc_id] = []
            self.conversations[self.current_doc_id].append({
                'question': question,
                'answer': answer
            })
    
    def clear_conversation(self):
        if self.current_doc_id and self.current_doc_id in self.conversations:
            self.conversations[self.current_doc_id] = []
    
    def query(self, question):
        if not self.is_ready():
            return "System not ready - check API key status."
        
        current_text = self.get_current_document()
        if not current_text:
            return "Please upload and select a document first."
            
        try:
            with st.spinner("Thinking..."):
                # Build conversation context
                conversation_history = self.get_conversation_history()
                history_context = ""
                if conversation_history:
                    history_context = "\n\nPrevious questions and answers:\n"
                    for i, conv in enumerate(conversation_history[-3:]):
                        history_context += f"Q: {conv['question']}\nA: {conv['answer']}\n\n"
                
                prompt = f"""Based ONLY on the following context:

{current_text}
{history_context}

Question: {question}

Answer based only on the context above:"""
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1
                )
                
                answer = response.choices[0].message.content
                self.add_to_conversation(question, answer)
                
                return answer
        except Exception as e:
            return f"Error: {str(e)}"

# Main App
st.set_page_config(page_title="Cram AI", layout="wide")

st.title("Cram AI")
st.markdown("Upload your study materials and chat with them")

# Initialize RAG system
if 'rag' not in st.session_state:
    st.session_state.rag = SimpleRAG()

rag = st.session_state.rag

# Sidebar for file management
with st.sidebar:
    st.header("📁 Documents")
    
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
            file_exists = any(doc['filename'] == uploaded_file.name for doc in rag.documents.values())
            
            if not file_exists:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    text = FileProcessor.process_file(uploaded_file)
                    
                    if text != "Unsupported file type" and len(text.strip()) > 0:
                        doc_id = str(uuid.uuid4())
                        rag.add_document(text, doc_id, uploaded_file.name)
                        st.success(f"✅ {uploaded_file.name}")
                    else:
                        st.error(f"❌ {uploaded_file.name}")
    
    # Document management
    if rag.documents:
        st.divider()
        st.subheader("Your Documents")
        
        doc_options = {doc_id: info['filename'] for doc_id, info in rag.documents.items()}
        if doc_options:
            selected_doc = st.selectbox(
                "Active document:",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                index=list(doc_options.keys()).index(rag.current_doc_id) if rag.current_doc_id in doc_options else 0
            )
            rag.switch_document(selected_doc)
            
            # Conversation controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    rag.clear_conversation()
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Doc", use_container_width=True):
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
    
    elif rag.is_ready() and not rag.documents:
        st.info("📁 Upload some documents in the sidebar to get started!")
    
    elif not rag.is_ready():
        st.warning("⚠️ System initializing...")

with col2:
    st.header("ℹ️ Info")
    if rag.documents:
        st.write(f"**Documents:** {len(rag.documents)}")
        current_conv = rag.get_conversation_history()
        st.write(f"**Messages:** {len(current_conv)}")
        
        if rag.get_current_document():
            doc_name = rag.documents[rag.current_doc_id]['filename']
            st.write(f"**Active:** {doc_name}")
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
