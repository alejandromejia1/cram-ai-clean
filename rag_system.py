import streamlit as st
from openai import OpenAI

class SimpleRAG:
    def __init__(self):
        self.documents = {}
        self.current_doc_id = None
        self.conversations = {}
        self.client = None
        self.initialized = False
        
        # Initialize without blocking the entire app
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            if 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
                
                # Check if it's the bad placeholder
                if "your_actual" in api_key or "your-real" in api_key:
                    # Don't show error in main interface
                    self.client = None
                    return
                    
                self.client = OpenAI(api_key=api_key)
                self.initialized = True
            else:
                # Don't show error in main interface
                self.client = None
        except Exception as e:
            # Don't show error in main interface
            self.client = None
    
    def is_ready(self):
        return self.client is not None and self.initialized
    
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
            return "Please configure your API key in the Streamlit secrets to enable AI responses."
        
        current_text = self.get_current_document()
        if not current_text:
            return "Please upload and select a document first."
            
        try:
            # Build conversation context
            conversation_history = self.get_conversation_history()
            
            # IMPROVED PROMPT ENGINEERING
            system_prompt = """You are a helpful study assistant. Follow these rules strictly:

1. If the user asks a question that can be answered using the provided context, answer based ONLY on that context
2. If the question cannot be answered from the context, say "I cannot find that information in the provided documents"
3. For normal conversation (thanks, hello, etc.), respond naturally without referencing the documents
4. NEVER make up information or code unless it's explicitly in the context
5. If you're asked to write code but no coding examples exist in the context, decline politely

Context:"""
            
            # Only include document context for substantive questions
            user_message = f"{question}"
            
            messages = [
                {"role": "system", "content": system_prompt + f"\n{current_text}"},
            ]
            
            # Add recent conversation history for context
            if conversation_history:
                for conv in conversation_history[-4:]:  # Last 4 exchanges
                    messages.append({"role": "user", "content": conv['question']})
                    messages.append({"role": "assistant", "content": conv['answer']})
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.1
            )
            
            answer = response.choices[0].message.content
            self.add_to_conversation(question, answer)
            
            return answer
        except Exception as e:
            return f"Error processing your request: {str(e)}"
