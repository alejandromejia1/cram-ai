import os
from openai import OpenAI
import streamlit as st

class SimpleRAG:
    def __init__(self):
        api_key = None
        
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
                st.success("🔑 API key loaded from Streamlit secrets")
            else:
                st.error("❌ No API key found in Streamlit secrets")
                self.client = None
                return
        except Exception as e:
            st.error(f"❌ Error accessing secrets: {str(e)}")
            self.client = None
            return
            
        if not api_key or "your_actual" in api_key or "your-real" in api_key or len(api_key) < 50:
            st.error("❌ Invalid API key format - check Streamlit secrets")
            self.client = None
            return
            
        try:
            self.client = OpenAI(api_key=api_key)
            self.client.models.list()
            st.success("✅ API key validated and working!")
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
            return "❌ OpenAI client not configured. Check API key in Streamlit secrets."
            
        try:
            if not self.current_document:
                return "📁 Please upload a document first."
            
            with st.spinner("🤔 Thinking..."):
                prompt = f"""Based ONLY on the following study materials, answer the question:

Study Materials:
{self.current_document}

Question: {question}

Answer:"""
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant. Answer based ONLY on the provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
