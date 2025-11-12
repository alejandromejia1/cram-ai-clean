import streamlit as st
from openai import OpenAI

class SimpleRAG:
    def __init__(self):
        # ONLY use Streamlit secrets - no .env fallback
        if 'OPENAI_API_KEY' not in st.secrets:
            st.error("❌ API key not found in Streamlit secrets")
            self.client = None
            return
            
        api_key = st.secrets['OPENAI_API_KEY']
        
        # Validate it's a real key
        if "your_actual" in api_key or "your-real" in api_key:
            st.error("❌ Invalid API key - contains placeholder text")
            self.client = None
            return
            
        try:
            self.client = OpenAI(api_key=api_key)
            st.success("✅ API key validated successfully!")
        except Exception as e:
            st.error(f"❌ API key validation failed: {str(e)}")
            self.client = None
            return
            
        self.current_document = ""
    
    def add_document(self, text, doc_id):
        if text and text != "Unsupported file type":
            self.current_document = text
    
    def query(self, question, n_results=3):
        if not self.client:
            return "OpenAI client not configured. Please check your API key in Streamlit secrets."
            
        try:
            if not self.current_document:
                return "Please upload a document first."
            
            with st.spinner("Finding answer..."):
                prompt = f"""Based on the following study materials, answer the question.

Study Materials:
{self.current_document}

Question: {question}

Answer:"""
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant. Answer based only on the provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
                
        except Exception as e:
            return f"Error: {str(e)}"
