import streamlit as st
from openai import OpenAI

class SimpleRAG:
    def __init__(self):
        st.write("🔍 DEBUG: Secrets available:", list(st.secrets.keys()))
        
        # DIRECT access to secrets - no try/except
        if 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
            st.write(f"📋 Key found: {api_key[:20]}...")
            
            # Check if it's the bad placeholder
            if "your_actual" in api_key or "your-real" in api_key:
                st.error("❌ BAD KEY: Contains placeholder text")
                self.client = None
                return
                
            try:
                self.client = OpenAI(api_key=api_key)
                # Test the key
                self.client.models.list()
                st.success("✅ API KEY VALIDATED AND WORKING!")
                self.current_document = ""
                return
            except Exception as e:
                st.error(f"❌ API Key failed: {str(e)}")
                self.client = None
                return
        else:
            st.error("❌ OPENAI_API_KEY not found in st.secrets")
            self.client = None
            return
    
    def add_document(self, text, doc_id):
        if text and text != "Unsupported file type":
            self.current_document = text
    
    def query(self, question, n_results=3):
        if not self.client:
            return "System not ready - API key issue above."
            
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
